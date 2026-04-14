"""by Audrey-Anne Beaudry Feb. 2026, modified by Caroline Woodard via GitHub Copilot, 2026-04-07"""

import argparse
import os
import sqlite3


def split_database_by_frame(input_db, output_db, start_frame, end_frame):
    # Ensure output directory exists
    output_dir = os.path.dirname(output_db)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    conn_in = sqlite3.connect(input_db)
    conn_out = sqlite3.connect(output_db)

    c_in = conn_in.cursor()
    c_out = conn_out.cursor()

    # Get tables
    c_in.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';""")
    tables = [row[0] for row in c_in.fetchall()]

    for table in tables:
        print(f"Processing table: {table}")

        # Recreate table
        c_in.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?;", (table,))
        create_stmt = c_in.fetchone()[0]
        c_out.execute(create_stmt)

        # Check columns
        c_in.execute(f'PRAGMA table_info("{table}");')
        columns = [col[1] for col in c_in.fetchall()]

        if "FRAMENUMBER" in columns:
            query = f'SELECT * FROM "{table}" WHERE FRAMENUMBER BETWEEN ? AND ?'
            rows = c_in.execute(query, (start_frame, end_frame))
        else:
            rows = c_in.execute(f'SELECT * FROM "{table}"')

        placeholders = ",".join(["?"] * len(columns))
        insert_query = f'INSERT INTO "{table}" VALUES ({placeholders})'

        for row in rows:
            c_out.execute(insert_query, row)

        conn_out.commit()

    conn_in.close()
    conn_out.close()

    print(f"Created {output_db}")


def _ask_if_missing(value, prompt):
    if value is not None:
        return value
    typed = input(prompt).strip()
    return typed if typed != "" else None


def main():
    parser = argparse.ArgumentParser(
        description="Create a new sqlite DB containing rows between two frame numbers."
    )
    parser.add_argument("--input-db", dest="input_db", help="Path to input sqlite file")
    parser.add_argument("--output-db", dest="output_db", help="Path to output sqlite file")
    parser.add_argument("--start-frame", dest="start_frame", type=int, help="First frame (inclusive)")
    parser.add_argument("--end-frame", dest="end_frame", type=int, help="Last frame (inclusive)")

    args = parser.parse_args()

    input_db = _ask_if_missing(args.input_db, "Input sqlite path: ")
    if not input_db:
        raise ValueError("Missing input database path.")
    if not os.path.exists(input_db):
        raise FileNotFoundError(f"Input database not found: {input_db}")

    output_db = _ask_if_missing(args.output_db, "Output sqlite path: ")
    if not output_db:
        root, ext = os.path.splitext(input_db)
        output_db = root + "_split" + ext
        print(f"No output path provided. Using: {output_db}")

    start_frame = args.start_frame
    if start_frame is None:
        start_frame = int(_ask_if_missing(None, "Start frame (inclusive): "))

    end_frame = args.end_frame
    if end_frame is None:
        end_frame = int(_ask_if_missing(None, "End frame (inclusive): "))

    if end_frame < start_frame:
        raise ValueError("end_frame must be greater than or equal to start_frame")

    split_database_by_frame(input_db, output_db, start_frame, end_frame)


if __name__ == "__main__":
    main()