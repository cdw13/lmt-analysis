#!/usr/bin/env python3
"""
Count occurrences of 1, 2, and 3 in a CSV file.

Usage:
    python tools/count_csv_123.py path/to/file.csv
"""

import argparse
import csv
from collections import Counter


def count_values_in_csv(csv_path):
    counts = Counter({"1": 0, "2": 0, "3": 0})

    with open(csv_path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            for cell in row:
                value = cell.strip()
                if value in counts:
                    counts[value] += 1

    return counts


def main():
    parser = argparse.ArgumentParser(
        description="Count how many times 1, 2, and 3 appear in a CSV file."
    )
    parser.add_argument("csv_file", help="Path to the CSV file")
    args = parser.parse_args()

    counts = count_values_in_csv(args.csv_file)

    print(f"File: {args.csv_file}")
    print(f"1: {counts['1']}")
    print(f"2: {counts['2']}")
    print(f"3: {counts['3']}")


if __name__ == "__main__":
    main()
