"""Transaction categorization and income source classification for EarnScore.

Guardrails:
- Internal transfers are strictly tagged as 'transfer' and NEVER classified as earned income.
- Refunds and chargeback reversals are classified as 'refund' and excluded from earned income.
- Known gig platforms and client types are recognized accurately.
- Unknown sources are explicitly labeled as 'Unknown'—never hallucinated or guessed.
"""

import re
from typing import Optional, Tuple
from src.data_pipeline.schemas import TransactionCategory, TransactionType


# Known platform mapping keywords to standard names
KNOWN_SOURCES = {
    "urbancompany": "UrbanCompany",
    "urban company": "UrbanCompany",
    "swiggy": "Swiggy",
    "zomato": "Zomato",
    "uber": "Uber",
    "ola": "Ola",
    "upwork": "Upwork",
    "fiverr": "Fiverr",
    "direct client": "Direct-Client",
    "direct-client": "Direct-Client",
    "eventhub": "EventHub",
    "wedmegood": "WedMeGood-Vendors",
    "local-gigs": "Local-Gigs",
    "local gigs": "Local-Gigs",
}

# Regex heuristics for descriptions/sources
TRANSFER_PATTERNS = [
    r"\btransfer\b",
    r"\bself\b",
    r"\bown\s+account\b",
    r"\bto\s+savings\b",
    r"\bfrom\s+savings\b",
    r"\bwallet\s+topup\b",
    r"\batm\s+withdrawal\b",
    r"\bcredit\s+card\s+payment\b",
]

REFUND_PATTERNS = [
    r"\brefund\b",
    r"\breversal\b",
    r"\bchargeback\b",
    r"\bcashback\b",
    r"\breturn\b",
]


def identify_source(source_raw: Optional[str], description_raw: Optional[str] = None) -> str:
    """Identifies and normalizes the source name from source or description fields.
    
    If unclassifiable, strictly returns 'Unknown' without hallucinating categories.
    """
    text_to_check = f"{source_raw or ''} {description_raw or ''}".lower()
    
    for key, normalized_name in KNOWN_SOURCES.items():
        if key in text_to_check:
            return normalized_name
            
    # If source_raw was provided and not recognized
    cleaned_source = (source_raw or "").strip()
    if cleaned_source and cleaned_source.lower() not in ["", "unknown", "nan", "none"]:
        # Return cleaned existing source if explicit, or Unknown if generic
        return cleaned_source
    
    return "Unknown"


def classify_category(
    tx_type: TransactionType,
    category_raw: Optional[str] = None,
    source: Optional[str] = None,
    description: Optional[str] = None,
) -> TransactionCategory:
    """Determines transaction category based on type, existing label, and descriptions.
    
    Guarantees:
    - Transfers and refunds are never classified as 'income'.
    """
    text = f"{category_raw or ''} {source or ''} {description or ''}".lower()

    # 1. Check for refunds/reversals
    for pat in REFUND_PATTERNS:
        if re.search(pat, text):
            return TransactionCategory.REFUND

    # 2. Check for internal transfers/movements
    for pat in TRANSFER_PATTERNS:
        if re.search(pat, text):
            return TransactionCategory.TRANSFER

    # 3. Check explicit category if supplied
    cleaned_cat = (category_raw or "").strip().lower()
    if cleaned_cat == "income":
        return TransactionCategory.INCOME if tx_type == TransactionType.CREDIT else TransactionCategory.EXPENSE
    if cleaned_cat == "expense":
        return TransactionCategory.EXPENSE
    if cleaned_cat == "transfer":
        return TransactionCategory.TRANSFER
    if cleaned_cat == "refund":
        return TransactionCategory.REFUND

    # 4. Default based on transaction type
    if tx_type == TransactionType.CREDIT:
        # A credit that is not a transfer or refund is classified as income
        return TransactionCategory.INCOME
    else:
        # A debit is an expense
        return TransactionCategory.EXPENSE


def is_earned_income(tx_type: TransactionType, category: TransactionCategory) -> bool:
    """Returns True if the transaction represents valid earned income.
    
    Strictly excludes:
    - Debits
    - Internal transfers
    - Refunds, reversals, or cashbacks
    """
    return tx_type == TransactionType.CREDIT and category == TransactionCategory.INCOME

