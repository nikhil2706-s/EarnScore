"""Command-line interface and end-to-end pipeline runner for Member 1.

Usage:
  python -m src.data_pipeline.pipeline data/raw/demo-stable-001.csv [--output path/to/output.json]

Guarantees:
- Emits clean, valid JSON object to stdout.
- Emits logging and diagnostic messages strictly to stderr.
- Fully validated against Member1FeaturePayload schema.
- Rejects multi-applicant conflicting CSVs, unreadable files, or invalid inputs safely.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from src.data_pipeline.cleaner import load_and_clean_csv
from src.data_pipeline.features import extract_features
from src.data_pipeline.schemas import Member1FeaturePayload


def run_pipeline(
    csv_path: Path,
    output_path: Optional[Path] = None,
    applicant_id: Optional[str] = None,
) -> Member1FeaturePayload:
    """Executes end-to-end processing: CSV -> Clean -> Features -> Validated Payload."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Input file not found: {csv_path}")

    # 1. Clean and normalize
    sys.stderr.write(f"[INFO] Ingesting and normalizing transactions from {csv_path}...\n")
    df_clean, audit = load_and_clean_csv(csv_path, default_applicant_id=applicant_id)

    if audit.exact_duplicates_removed > 0:
        sys.stderr.write(f"[INFO] Removed {audit.exact_duplicates_removed} exact duplicate records.\n")

    if audit.has_conflicts:
        sys.stderr.write(f"[WARN] Quarantined {len(audit.conflicting_duplicate_ids)} conflicting duplicate transaction IDs.\n")

    if audit.invalid_rows_flagged:
        sys.stderr.write(f"[WARN] Flagged {len(audit.invalid_rows_flagged)} invalid rows during validation.\n")

    if df_clean.empty:
        raise ValueError("No valid normalized transactions available after cleaning.")

    # 2. Check for single applicant consistency
    distinct_applicants = df_clean["applicant_id"].unique().tolist()
    if len(distinct_applicants) > 1 and not applicant_id:
        raise ValueError(
            f"Input file contains multiple distinct applicant IDs ({distinct_applicants}). "
            "Please specify a single target applicant."
        )

    target_applicant = applicant_id or distinct_applicants[0]

    # 3. Feature extraction & aggregation
    sys.stderr.write(f"[INFO] Extracting financial features for applicant: {target_applicant}...\n")
    payload = extract_features(df_clean, applicant_id=target_applicant)

    # 4. Save to file if requested
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(payload.model_dump_json(indent=2))
        sys.stderr.write(f"[INFO] Feature payload successfully written to {output_path}\n")

    return payload


def main() -> None:
    parser = argparse.ArgumentParser(
        description="EarnScore Member 1 Data Pipeline: Process raw transaction CSV into financial features JSON."
    )
    parser.add_argument("csv_path", type=Path, help="Path to input transaction CSV file")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Optional destination path to save output JSON",
    )
    parser.add_argument(
        "--applicant-id",
        "-a",
        type=str,
        default=None,
        help="Target applicant ID (optional if CSV contains exactly one applicant)",
    )

    args = parser.parse_args()

    try:
        payload = run_pipeline(
            csv_path=args.csv_path,
            output_path=args.output,
            applicant_id=args.applicant_id,
        )
        # Exactly one valid JSON object to stdout
        sys.stdout.write(payload.model_dump_json(indent=2) + "\n")
        sys.stdout.flush()
    except Exception as e:
        sys.stderr.write(f"[ERROR] Pipeline execution failed: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

