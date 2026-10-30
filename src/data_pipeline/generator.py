"""Synthetic transaction dataset generator for EarnScore.

CRITICAL DISCLAIMER:
All generated data is strictly SYNTHETIC / SIMULATED for hackathon demonstration.
No real personal, banking, or credit data is used, modeled, or claimed.

Personas generated:
- demo-stable-001: Stable gig worker with consistent multi-platform income (e.g. Uber + Swiggy)
- demo-volatile-002: New/irregular freelancer with high volatility, gaps, and shorter history
- demo-seasonal-003: Seasonal worker with distinct peak and off-peak earning months
"""

import csv
import datetime as _dt
import random
from pathlib import Path
from typing import Dict, List, Optional

from src.data_pipeline.schemas import (
    NormalizedTransaction,
    TransactionCategory,
    TransactionType,
)


# Fixed random seed for deterministic generation across runs
GLOBAL_SEED = 42

# Currency / Context: Indian Rupee (INR)
# Date anchor: Current simulation date is October 2026.
# Latest fully completed month: September 2026 (2026-09-30).
SIMULATION_END_DATE = _dt.date(2026, 9, 30)


def _generate_date_range(end_date: _dt.date, months_back: int) -> List[_dt.date]:
    """Generate all calendar dates over a given number of past months up to end_date."""
    # Approximate start date going back months_back months (30.4 days per month avg)
    # Ensure exact 1st of month
    start_year = end_date.year - ((months_back - 1) // 12)
    start_month = end_date.month - ((months_back - 1) % 12)
    if start_month <= 0:
        start_month += 12
        start_year -= 1
    start_date = _dt.date(start_year, start_month, 1)

    dates = []
    curr = start_date
    while curr <= end_date:
        dates.append(curr)
        curr += _dt.timedelta(days=1)
    return dates


def generate_stable_worker_transactions(
    applicant_id: str = "demo-stable-001",
    seed: int = 101,
) -> List[NormalizedTransaction]:
    """Generates 12 months of consistent multi-source gig income and regular expenses.
    
    Income sources:
    - UrbanCompany: Weekly home services payout (~Rs 6,000 - 9,500)
    - Swiggy: Weekly delivery payout (~Rs 3,500 - 6,000)
    - Occasional tips / incentives (~Rs 500 - 1,500)
    
    Expenses:
    - Rent, groceries, utilities, vehicle fuel/maintenance.
    """
    rng = random.Random(seed)
    transactions: List[NormalizedTransaction] = []
    tx_counter = 1

    dates = _generate_date_range(SIMULATION_END_DATE, months_back=12)
    current_month = None

    for d in dates:
        # Monthly fixed expenses on the 5th
        if d.day == 5:
            # Rent
            transactions.append(
                NormalizedTransaction(
                    transaction_id=f"{applicant_id}-TX-{tx_counter:05d}",
                    applicant_id=applicant_id,
                    date=d,
                    amount=12000.00,
                    type=TransactionType.DEBIT,
                    category=TransactionCategory.EXPENSE,
                    source="UPI-Rent",
                    description="Monthly house rent transfer via UPI",
                    balance=None,
                )
            )
            tx_counter += 1
            # Electricity / Utilities
            transactions.append(
                NormalizedTransaction(
                    transaction_id=f"{applicant_id}-TX-{tx_counter:05d}",
                    applicant_id=applicant_id,
                    date=d,
                    amount=round(rng.uniform(1400.0, 2200.0), 2),
                    type=TransactionType.DEBIT,
                    category=TransactionCategory.EXPENSE,
                    source="Electricity-Bill",
                    description="Monthly utility electricity bill payment",
                    balance=None,
                )
            )
            tx_counter += 1

        # Weekly payouts:
        # Every Monday (weekday == 0): UrbanCompany payout
        if d.weekday() == 0:
            uc_amt = round(rng.uniform(6500.0, 9500.0), 2)
            transactions.append(
                NormalizedTransaction(
                    transaction_id=f"{applicant_id}-TX-{tx_counter:05d}",
                    applicant_id=applicant_id,
                    date=d,
                    amount=uc_amt,
                    type=TransactionType.CREDIT,
                    category=TransactionCategory.INCOME,
                    source="UrbanCompany",
                    description="Weekly partner earnings settlement - UrbanCompany",
                    balance=None,
                )
            )
            tx_counter += 1

        # Every Wednesday (weekday == 2): Swiggy delivery payout
        if d.weekday() == 2:
            swiggy_amt = round(rng.uniform(3800.0, 5800.0), 2)
            transactions.append(
                NormalizedTransaction(
                    transaction_id=f"{applicant_id}-TX-{tx_counter:05d}",
                    applicant_id=applicant_id,
                    date=d,
                    amount=swiggy_amt,
                    type=TransactionType.CREDIT,
                    category=TransactionCategory.INCOME,
                    source="Swiggy",
                    description="Weekly delivery partner payout - Swiggy",
                    balance=None,
                )
            )
            tx_counter += 1

        # Weekly fuel & vehicle maintenance (Thursdays)
        if d.weekday() == 3:
            fuel_amt = round(rng.uniform(600.0, 1100.0), 2)
            transactions.append(
                NormalizedTransaction(
                    transaction_id=f"{applicant_id}-TX-{tx_counter:05d}",
                    applicant_id=applicant_id,
                    date=d,
                    amount=fuel_amt,
                    type=TransactionType.DEBIT,
                    category=TransactionCategory.EXPENSE,
                    source="Fuel-Station",
                    description="Petrol pump fuel payment UPI",
                    balance=None,
                )
            )
            tx_counter += 1

        # Frequent daily living expenses / groceries (~40% of days)
        if rng.random() < 0.45:
            grocery_amt = round(rng.uniform(250.0, 950.0), 2)
            transactions.append(
                NormalizedTransaction(
                    transaction_id=f"{applicant_id}-TX-{tx_counter:05d}",
                    applicant_id=applicant_id,
                    date=d,
                    amount=grocery_amt,
                    type=TransactionType.DEBIT,
                    category=TransactionCategory.EXPENSE,
                    source="UPI-Groceries",
                    description="Kirana store / local supermarket purchase",
                    balance=None,
                )
            )
            tx_counter += 1

        # Occasional incentive bonus (1-2 times per month, weekend)
        if d.weekday() == 6 and rng.random() < 0.35:
            bonus_amt = round(rng.uniform(800.0, 2000.0), 2)
            transactions.append(
                NormalizedTransaction(
                    transaction_id=f"{applicant_id}-TX-{tx_counter:05d}",
                    applicant_id=applicant_id,
                    date=d,
                    amount=bonus_amt,
                    type=TransactionType.CREDIT,
                    category=TransactionCategory.INCOME,
                    source="UrbanCompany",
                    description="High performance weekend milestone incentive",
                    balance=None,
                )
            )
            tx_counter += 1

    return transactions


def generate_volatile_worker_transactions(
    applicant_id: str = "demo-volatile-002",
    seed: int = 202,
) -> List[NormalizedTransaction]:
    """Generates an irregular/new freelancer with gaps, limited history (5 months), and volatility.
    
    Income:
    - Freelance design/writing clients (erratic dates and lumps: Rs 8,000 to Rs 32,000)
    - One month with zero income (dry spell)
    - High month-to-month coefficient of variation
    """
    rng = random.Random(seed)
    transactions: List[NormalizedTransaction] = []
    tx_counter = 1

    # Only 5 observed months (May 2026 to Sep 2026)
    dates = _generate_date_range(SIMULATION_END_DATE, months_back=5)

    for d in dates:
        # Month 1 (May): High freelance payout (Rs 28,000) on May 12
        if d.month == 5 and d.day == 12:
            transactions.append(
                NormalizedTransaction(
                    transaction_id=f"{applicant_id}-TX-{tx_counter:05d}",
                    applicant_id=applicant_id,
                    date=d,
                    amount=28500.00,
                    type=TransactionType.CREDIT,
                    category=TransactionCategory.INCOME,
                    source="Upwork",
                    description="Client project milestone release - UI Wireframes",
                    balance=None,
                )
            )
            tx_counter += 1

        # Month 2 (June): Lower freelance payout (Rs 9,500) on June 20
        if d.month == 6 and d.day == 20:
            transactions.append(
                NormalizedTransaction(
                    transaction_id=f"{applicant_id}-TX-{tx_counter:05d}",
                    applicant_id=applicant_id,
                    date=d,
                    amount=9500.00,
                    type=TransactionType.CREDIT,
                    category=TransactionCategory.INCOME,
                    source="Direct-Client",
                    description="Graphic design asset pack delivery",
                    balance=None,
                )
            )
            tx_counter += 1

        # Month 3 (July): Dry spell! 0 income transactions, only recurring expenses.

        # Month 4 (August): Huge lump sum on Aug 28 (Rs 42,000)
        if d.month == 8 and d.day == 28:
            transactions.append(
                NormalizedTransaction(
                    transaction_id=f"{applicant_id}-TX-{tx_counter:05d}",
                    applicant_id=applicant_id,
                    date=d,
                    amount=42000.00,
                    type=TransactionType.CREDIT,
                    category=TransactionCategory.INCOME,
                    source="Fiverr",
                    description="E-commerce web redesign contract settlement",
                    balance=None,
                )
            )
            tx_counter += 1

        # Month 5 (September): Small payout (Rs 7,000)
        if d.month == 9 and d.day == 15:
            transactions.append(
                NormalizedTransaction(
                    transaction_id=f"{applicant_id}-TX-{tx_counter:05d}",
                    applicant_id=applicant_id,
                    date=d,
                    amount=7000.00,
                    type=TransactionType.CREDIT,
                    category=TransactionCategory.INCOME,
                    source="Direct-Client",
                    description="Landing page maintenance retainer",
                    balance=None,
                )
            )
            tx_counter += 1

        # Fixed rent and co-working on the 7th of each active month
        if d.day == 7:
            transactions.append(
                NormalizedTransaction(
                    transaction_id=f"{applicant_id}-TX-{tx_counter:05d}",
                    applicant_id=applicant_id,
                    date=d,
                    amount=15000.00,
                    type=TransactionType.DEBIT,
                    category=TransactionCategory.EXPENSE,
                    source="Bank-Transfer",
                    description="Monthly co-living and desk space rent",
                    balance=None,
                )
            )
            tx_counter += 1

        # High variable lifestyle / software subscriptions
        if d.day == 10:
            transactions.append(
                NormalizedTransaction(
                    transaction_id=f"{applicant_id}-TX-{tx_counter:05d}",
                    applicant_id=applicant_id,
                    date=d,
                    amount=3499.00,
                    type=TransactionType.DEBIT,
                    category=TransactionCategory.EXPENSE,
                    source="Software-Subscription",
                    description="Adobe Creative Cloud / Figma subscription",
                    balance=None,
                )
            )
            tx_counter += 1

        # Regular living expenses
        if rng.random() < 0.35:
            transactions.append(
                NormalizedTransaction(
                    transaction_id=f"{applicant_id}-TX-{tx_counter:05d}",
                    applicant_id=applicant_id,
                    date=d,
                    amount=round(rng.uniform(300.0, 1400.0), 2),
                    type=TransactionType.DEBIT,
                    category=TransactionCategory.EXPENSE,
                    source="UPI-Payment",
                    description="Food delivery and cafe work spend",
                    balance=None,
                )
            )
            tx_counter += 1

    return transactions


def generate_seasonal_worker_transactions(
    applicant_id: str = "demo-seasonal-003",
    seed: int = 303,
) -> List[NormalizedTransaction]:
    """Generates 12 months for a seasonal event / festival & tourism gig worker.
    
    Seasonal pattern:
    - Peak Months: Oct, Nov, Dec, Jan, Feb (festival & wedding season, tourism) -> Rs 45,000 - 65,000/mo
    - Off-peak Months: Mar, Apr, May, Jun, Jul, Aug, Sep -> Rs 8,000 - 16,000/mo (intermittent jobs)
    """
    rng = random.Random(seed)
    transactions: List[NormalizedTransaction] = []
    tx_counter = 1

    dates = _generate_date_range(SIMULATION_END_DATE, months_back=12)

    for d in dates:
        # Determine if peak month
        # Festival & wedding peak: Oct (10), Nov (11), Dec (12), Jan (1), Feb (2)
        is_peak = d.month in [10, 11, 12, 1, 2]

        # Monthly basic living expense on 3rd
        if d.day == 3:
            transactions.append(
                NormalizedTransaction(
                    transaction_id=f"{applicant_id}-TX-{tx_counter:05d}",
                    applicant_id=applicant_id,
                    date=d,
                    amount=9500.00,
                    type=TransactionType.DEBIT,
                    category=TransactionCategory.EXPENSE,
                    source="UPI-Landlord",
                    description="Monthly accommodation rent payment",
                    balance=None,
                )
            )
            tx_counter += 1

        # Income generation:
        if is_peak:
            # Frequent event/catering & photo gigs during weekends & mid-week
            if d.weekday() in [4, 5, 6] and rng.random() < 0.65:
                amt = round(rng.uniform(4000.0, 8500.0), 2)
                source = rng.choice(["EventHub", "WedMeGood-Vendors", "UrbanCompany-Events"])
                transactions.append(
                    NormalizedTransaction(
                        transaction_id=f"{applicant_id}-TX-{tx_counter:05d}",
                        applicant_id=applicant_id,
                        date=d,
                        amount=amt,
                        type=TransactionType.CREDIT,
                        category=TransactionCategory.INCOME,
                        source=source,
                        description="Event coordination and photography milestone payout",
                        balance=None,
                    )
                )
                tx_counter += 1
        else:
            # Off-peak: Only 1-2 small gigs every two weeks
            if d.weekday() == 5 and rng.random() < 0.35:
                amt = round(rng.uniform(2000.0, 4200.0), 2)
                transactions.append(
                    NormalizedTransaction(
                        transaction_id=f"{applicant_id}-TX-{tx_counter:05d}",
                        applicant_id=applicant_id,
                        date=d,
                        amount=amt,
                        type=TransactionType.CREDIT,
                        category=TransactionCategory.INCOME,
                        source="Local-Gigs",
                        description="Weekend local equipment support gig payout",
                        balance=None,
                    )
                )
                tx_counter += 1

        # Regular daily expenses
        if rng.random() < 0.30:
            exp_amt = round(rng.uniform(200.0, 750.0), 2)
            transactions.append(
                NormalizedTransaction(
                    transaction_id=f"{applicant_id}-TX-{tx_counter:05d}",
                    applicant_id=applicant_id,
                    date=d,
                    amount=exp_amt,
                    type=TransactionType.DEBIT,
                    category=TransactionCategory.EXPENSE,
                    source="UPI-Merchant",
                    description="Daily meals and transportation",
                    balance=None,
                )
            )
            tx_counter += 1

    return transactions


def export_transactions_to_csv(
    transactions: List[NormalizedTransaction],
    filepath: Path,
) -> None:
    """Exports normalized transactions to a standard CSV file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "transaction_id",
        "applicant_id",
        "date",
        "amount",
        "type",
        "category",
        "source",
        "description",
        "balance",
    ]

    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for tx in transactions:
            writer.writerow({
                "transaction_id": tx.transaction_id,
                "applicant_id": tx.applicant_id,
                "date": tx.date.isoformat(),
                "amount": f"{tx.amount:.2f}",
                "type": tx.type.value,
                "category": tx.category.value,
                "source": tx.source,
                "description": tx.description,
                "balance": f"{tx.balance:.2f}" if tx.balance is not None else "",
            })


def generate_all_datasets(output_dir: Path) -> Dict[str, int]:
    """Generates all 3 demo persona datasets and writes CSVs to output_dir."""
    generators = {
        "demo-stable-001": generate_stable_worker_transactions("demo-stable-001", seed=GLOBAL_SEED + 1),
        "demo-volatile-002": generate_volatile_worker_transactions("demo-volatile-002", seed=GLOBAL_SEED + 2),
        "demo-seasonal-003": generate_seasonal_worker_transactions("demo-seasonal-003", seed=GLOBAL_SEED + 3),
    }

    counts = {}
    for applicant_id, tx_list in generators.items():
        csv_path = output_dir / f"{applicant_id}.csv"
        export_transactions_to_csv(tx_list, csv_path)
        counts[applicant_id] = len(tx_list)

    return counts


if __name__ == "__main__":
    raw_dir = Path("data/raw")
    results = generate_all_datasets(raw_dir)
    print("Generated synthetic persona datasets:")
    for pid, count in results.items():
        print(f"  {pid}: {count} records written to data/raw/{pid}.csv")

