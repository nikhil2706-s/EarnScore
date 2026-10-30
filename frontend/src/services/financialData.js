import Papa from 'papaparse';

const round = value => Math.round(value * 100) / 100;

export async function extractFinancialData(file) {
  const text = await file.text();

  const result = Papa.parse(text, {
    header: true,
    skipEmptyLines: 'greedy',
    transformHeader: header => header.replace(/^\uFEFF/, '').trim(),
  });

  if (result.errors.length) {
    throw new Error(
      `CSV parsing failed at row ${result.errors[0].row ?? 'unknown'}: ${result.errors[0].message}`
    );
  }

  const required = ['date', 'amount', 'type', 'category', 'source'];
  const headers = result.meta.fields ?? [];

  if (!required.every(column => headers.includes(column))) {
    throw new Error('CSV is missing required financial columns');
  }

  const monthly = new Map();
  const sources = new Map();
  let validTransactions = 0;
  let rejectedTransactions = 0;

  for (const row of result.data) {
    const date = String(row.date ?? '').trim();
    const amountText = String(row.amount ?? '').trim();
    const amount = Number(amountText);
    const type = String(row.type ?? '').trim().toLowerCase();
    const category = String(row.category ?? '').trim().toLowerCase();
    const source = String(row.source ?? '').trim() || 'Unknown';

    const validDate =
      /^\d{4}-\d{2}-\d{2}$/.test(date) &&
      !Number.isNaN(Date.parse(`${date}T00:00:00Z`));

    const validAmount =
      amountText !== '' &&
      Number.isFinite(amount) &&
      amount >= 0;

    const isIncome = type === 'credit' && category === 'income';
    const isExpense = type === 'debit' && category === 'expense';

    if (!validDate || !validAmount || (!isIncome && !isExpense)) {
      rejectedTransactions++;
      continue;
    }

    const month = date.slice(0, 7);

    if (!monthly.has(month)) {
      monthly.set(month, { month, income: 0, expenses: 0 });
    }

    const item = monthly.get(month);

    if (isIncome) {
      item.income += amount;
      sources.set(source, (sources.get(source) ?? 0) + amount);
    } else {
      item.expenses += amount;
    }

    validTransactions++;
  }

  if (validTransactions === 0) {
    throw new Error('No valid income or expense transactions found');
  }

  const timeline = [...monthly.values()]
    .sort((a, b) => a.month.localeCompare(b.month))
    .map(item => ({
      month: item.month,
      income: round(item.income),
      expenses: round(item.expenses),
      netCashFlow: round(item.income - item.expenses),
    }));

  const incomeSources = [...sources.entries()]
    .map(([name, value]) => ({ name, value: round(value) }))
    .sort((a, b) => b.value - a.value);

  return {
    timeline,
    incomeSources,
    validation: {
      totalTransactions: result.data.length,
      validTransactions,
      rejectedTransactions,
    },
  };
}
