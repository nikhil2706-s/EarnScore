import {
  ResponsiveContainer, BarChart, Bar, LineChart, Line,
  PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend
} from 'recharts';

const COLORS = ['#15803d', '#22c55e', '#86efac', '#0d9488', '#94a3b8', '#f59e0b'];

const formatMoney = value =>
  new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(value);

export function FinancialCharts({ financialData }) {
  const timeline = financialData?.timeline ?? [];
  const sources = financialData?.incomeSources ?? [];

  if (!timeline.length) {
    return (
      <p className="empty-state-text">
        Upload a transaction CSV or select a demo worker to view financial evidence.
      </p>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', width: '100%', minWidth: 0 }}>
      <div>
        <h3>Monthly Income vs Expenses</h3>
        <div style={{ width: '100%', minWidth: 0, height: 260 }}>
          <ResponsiveContainer width="100%" height="100%" minWidth={0}>
            <BarChart data={timeline}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis tickFormatter={value => `₹${Math.round(value / 1000)}k`} />
              <Tooltip formatter={formatMoney} />
              <Legend />
              <Bar dataKey="income" name="Income" fill="#15803d" radius={[4, 4, 0, 0]} />
              <Bar dataKey="expenses" name="Expenses" fill="#86efac" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div>
        <h3>Net Cash-Flow Trend</h3>
        <div style={{ width: '100%', minWidth: 0, height: 250 }}>
          <ResponsiveContainer width="100%" height="100%" minWidth={0}>
            <LineChart data={timeline}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis tickFormatter={value => `₹${Math.round(value / 1000)}k`} />
              <Tooltip formatter={formatMoney} />
              <Line
                type="monotone"
                dataKey="netCashFlow"
                name="Net Cash Flow"
                stroke="#15803d"
                strokeWidth={3}
                dot={{ r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div>
        <h3>Platform Income Breakdown</h3>
        {sources.length ? (
          <div style={{ width: '100%', minWidth: 0, height: 280 }}>
            <ResponsiveContainer width="100%" height="100%" minWidth={0}>
              <PieChart>
                <Pie
                  data={sources}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={55}
                  outerRadius={90}
                  paddingAngle={2}
                >
                  {sources.map((source, index) => (
                    <Cell key={source.name} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={formatMoney} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p>No categorized income sources available.</p>
        )}
      </div>
    </div>
  );
}
