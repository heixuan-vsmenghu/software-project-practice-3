"""Generate a reproducible Fortune 500-like sample dataset for fallback use.

This script is kept as a backup tool. It does not overwrite an existing
fortune500.csv unless --force is provided.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


COMPANIES = [
    "General Motors",
    "Exxon Mobil",
    "Ford Motor",
    "General Electric",
    "IBM",
    "Chevron",
    "AT&T",
    "Boeing",
    "Coca-Cola",
    "Microsoft",
]


def build_rows():
    rows = []
    for year in range(1955, 1965):
        for rank, company in enumerate(COMPANIES, start=1):
            revenue = round(1000 + (year - 1955) * 130 + (11 - rank) * 85, 1)
            if (year + rank) % 13 == 0:
                profit = "N.A."
            else:
                profit = round(revenue * (0.04 + (rank % 4) * 0.01) - rank * 1.7, 1)
            rows.append(
                {
                    "year": year,
                    "rank": rank,
                    "company": company,
                    "revenue": revenue,
                    "profit": profit,
                }
            )
    return rows


def write_sample(output_path: Path, force: bool = False):
    if output_path.exists() and not force:
        raise FileExistsError(
            f"{output_path} already exists. Use --force only if you want to replace it."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["year", "rank", "company", "revenue", "profit"])
        writer.writeheader()
        writer.writerows(build_rows())


def main():
    parser = argparse.ArgumentParser(description="Generate a Fortune 500-like sample CSV.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "fortune500.csv",
        help="Output CSV path.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite the output file.")
    args = parser.parse_args()

    write_sample(args.output, force=args.force)
    print(f"Sample data written to {args.output}")


if __name__ == "__main__":
    main()
