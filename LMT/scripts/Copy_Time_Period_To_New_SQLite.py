#!/usr/bin/env python3
"""
created by Caroline Woodard via GitHub Copilot, 2026-04-01
Copy a selected time period from a Live Mouse Tracker sqlite database into a new sqlite database.

Usage examples:

1) Frame range:
python LMT/scripts/Copy_Time_Period_To_New_SQLite.py \
    --input /path/to/source.sqlite \
    --output /path/to/period.sqlite \
    --start-frame 10000 \
    --end-frame 50000

2) Datetime range (local time, format: YYYY-mm-dd HH:MM:SS):
python LMT/scripts/Copy_Time_Period_To_New_SQLite.py \
    --input /path/to/source.sqlite \
    --output /path/to/period.sqlite \
    --start-time "2026-03-30 11:10:36" \
    --end-time "2026-03-30 11:48:57"
"""

import argparse
import datetime
import os
import sqlite3
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import simpledialog


def parse_args():
    parser = argparse.ArgumentParser(
        description="Copy a selected time period from one sqlite DB to another."
    )
    parser.add_argument("--input", required=False, default=None, help="Source sqlite file")
    parser.add_argument("--output", required=False, default=None, help="Destination sqlite file")

    parser.add_argument("--start-frame", type=int, default=None, help="First frame to keep (inclusive)")
    parser.add_argument("--end-frame", type=int, default=None, help="Last frame to keep (inclusive)")

    parser.add_argument(
        "--start-time",
        default=None,
        help='Start datetime (inclusive), format "YYYY-mm-dd HH:MM:SS"',
    )
    parser.add_argument(
        "--end-time",
        default=None,
        help='End datetime (inclusive), format "YYYY-mm-dd HH:MM:SS"',
    )

    return parser.parse_args()


def choose_input_database(initial_path=None):
    root = tk.Tk()
    root.withdraw()
    root.update()

    filename = askopenfilename(
        title="Select source sqlite database",
        initialdir=initial_path,
        filetypes=(("sqlite files", "*.sqlite *.db"), ("all files", "*.*")),
    )

    root.destroy()
    return filename if filename else None


def choose_output_database(initial_path=None):
    root = tk.Tk()
    root.withdraw()
    root.update()

    filename = asksaveasfilename(
        title="Select destination sqlite database",
        initialdir=initial_path,
        defaultextension=".sqlite",
        filetypes=(("sqlite files", "*.sqlite *.db"), ("all files", "*.*")),
    )

    root.destroy()
    return filename if filename else None


def build_non_destructive_output_path(output_db):
    if not os.path.exists(output_db):
        return output_db

    root, ext = os.path.splitext(output_db)
    index = 1
    while True:
        candidate = "{}_{}{}".format(root, index, ext)
        if not os.path.exists(candidate):
            return candidate
        index += 1


def datetime_to_epoch_ms(dt_text):
    dt = datetime.datetime.strptime(dt_text, "%Y-%m-%d %H:%M:%S")
    return int(dt.timestamp() * 1000)


def validate_time_selection(args):
    frame_mode = args.start_frame is not None or args.end_frame is not None
    time_mode = args.start_time is not None or args.end_time is not None

    if frame_mode and time_mode:
        raise ValueError("Use either frame range or datetime range, not both")

    if not frame_mode and not time_mode:
        raise ValueError("You must provide either frame range or datetime range")

    if frame_mode and (args.start_frame is None or args.end_frame is None):
        raise ValueError("When using frame mode, provide both --start-frame and --end-frame")

    if time_mode and (args.start_time is None or args.end_time is None):
        raise ValueError("When using datetime mode, provide both --start-time and --end-time")


def get_frame_limits(src_conn):
    cur = src_conn.cursor()
    cur.execute("SELECT MIN(FRAMENUMBER), MAX(FRAMENUMBER) FROM FRAME")
    row = cur.fetchone()
    if row is None or row[0] is None or row[1] is None:
        raise ValueError("Could not read frame bounds from FRAME table")
    return int(row[0]), int(row[1])


def get_timestamp_limits(src_conn):
    cur = src_conn.cursor()
    cur.execute("SELECT MIN(TIMESTAMP), MAX(TIMESTAMP) FROM FRAME")
    row = cur.fetchone()
    if row is None or row[0] is None or row[1] is None:
        raise ValueError("Could not read timestamp bounds from FRAME table")
    return int(row[0]), int(row[1])


def choose_time_window_interactive(src_conn):
    min_frame, max_frame = get_frame_limits(src_conn)
    min_ts, max_ts = get_timestamp_limits(src_conn)

    default_start_dt = datetime.datetime.fromtimestamp(min_ts / 1000).strftime("%Y-%m-%d %H:%M:%S")
    default_end_dt = datetime.datetime.fromtimestamp(max_ts / 1000).strftime("%Y-%m-%d %H:%M:%S")

    root = tk.Tk()
    root.withdraw()
    root.update()

    mode = simpledialog.askstring(
        "Time window mode",
        "Choose mode:\n- Type 'frame' for frame numbers\n- Type 'time' for datetime\n",
        initialvalue="frame",
        parent=root,
    )

    if mode is None:
        root.destroy()
        raise ValueError("No time window mode selected")

    mode = mode.strip().lower()

    if mode == "time":
        start_text = simpledialog.askstring(
            "Start time",
            'Enter start datetime (YYYY-mm-dd HH:MM:SS):',
            initialvalue=default_start_dt,
            parent=root,
        )
        end_text = simpledialog.askstring(
            "End time",
            'Enter end datetime (YYYY-mm-dd HH:MM:SS):',
            initialvalue=default_end_dt,
            parent=root,
        )

        root.destroy()

        if start_text is None or end_text is None:
            raise ValueError("Start/end datetime not provided")

        start_ts = datetime_to_epoch_ms(start_text)
        end_ts = datetime_to_epoch_ms(end_text)
        start_frame, end_frame = get_frame_bounds_from_time(src_conn, start_text, end_text)
        return start_frame, end_frame, start_ts, end_ts

    start_frame = simpledialog.askinteger(
        "Start frame",
        "Enter start frame (inclusive):",
        initialvalue=min_frame,
        minvalue=min_frame,
        maxvalue=max_frame,
        parent=root,
    )
    end_frame = simpledialog.askinteger(
        "End frame",
        "Enter end frame (inclusive):",
        initialvalue=max_frame,
        minvalue=min_frame,
        maxvalue=max_frame,
        parent=root,
    )

    root.destroy()

    if start_frame is None or end_frame is None:
        raise ValueError("Start/end frame not provided")

    return int(start_frame), int(end_frame), None, None


def get_frame_bounds_from_time(src_conn, start_time_text, end_time_text):
    start_ms = datetime_to_epoch_ms(start_time_text)
    end_ms = datetime_to_epoch_ms(end_time_text)

    if end_ms < start_ms:
        raise ValueError("end-time must be >= start-time")

    cur = src_conn.cursor()

    cur.execute(
        """
        SELECT MIN(FRAMENUMBER), MAX(FRAMENUMBER)
        FROM FRAME
        WHERE TIMESTAMP >= ? AND TIMESTAMP <= ?
        """,
        (start_ms, end_ms),
    )
    row = cur.fetchone()

    if row is None or row[0] is None or row[1] is None:
        raise ValueError("No FRAME rows found in the provided datetime window")

    return int(row[0]), int(row[1])


def table_columns(conn, table_name):
    cur = conn.cursor()
    cur.execute('PRAGMA table_info("{}")'.format(table_name.replace('"', '""')))
    return [row[1] for row in cur.fetchall()]


def create_schema(src_conn, dst_conn):
    cur = src_conn.cursor()

    cur.execute(
        """
        SELECT name, sql
        FROM sqlite_master
        WHERE type='table'
          AND name NOT LIKE 'sqlite_%'
          AND sql IS NOT NULL
        ORDER BY name
        """
    )
    tables = cur.fetchall()

    for _, create_sql in tables:
        dst_conn.execute(create_sql)

    dst_conn.commit()


def copy_table_data(src_conn, dst_conn, table_name, start_frame, end_frame, start_ts, end_ts):
    cols = table_columns(src_conn, table_name)

    where_clause = None
    params = ()

    if "FRAMENUMBER" in cols:
        where_clause = "FRAMENUMBER >= ? AND FRAMENUMBER <= ?"
        params = (start_frame, end_frame)
    elif "STARTFRAME" in cols and "ENDFRAME" in cols:
        where_clause = "ENDFRAME >= ? AND STARTFRAME <= ?"
        params = (start_frame, end_frame)
    elif "STARTFRAME" in cols:
        where_clause = "STARTFRAME >= ? AND STARTFRAME <= ?"
        params = (start_frame, end_frame)
    elif "ENDFRAME" in cols:
        where_clause = "ENDFRAME >= ? AND ENDFRAME <= ?"
        params = (start_frame, end_frame)
    elif "TIMESTAMP" in cols and start_ts is not None and end_ts is not None:
        where_clause = "TIMESTAMP >= ? AND TIMESTAMP <= ?"
        params = (start_ts, end_ts)

    if where_clause is None:
        sql = 'INSERT INTO "{tbl}" SELECT * FROM main_src."{tbl}"'.format(
            tbl=table_name.replace('"', '""')
        )
        dst_conn.execute(sql)
    else:
        sql = 'INSERT INTO "{tbl}" SELECT * FROM main_src."{tbl}" WHERE {where}'.format(
            tbl=table_name.replace('"', '""'),
            where=where_clause,
        )
        dst_conn.execute(sql, params)


def copy_selected_period(input_db, output_db, start_frame, end_frame, start_ts=None, end_ts=None):
    if not os.path.exists(input_db):
        raise FileNotFoundError("Input sqlite file not found: {}".format(input_db))

    final_output_db = build_non_destructive_output_path(output_db)

    src_conn = sqlite3.connect(input_db)
    dst_conn = sqlite3.connect(final_output_db)

    try:
        print("Creating schema...")
        create_schema(src_conn, dst_conn)

        print("Copying table data...")
        dst_conn.execute("ATTACH DATABASE ? AS main_src", (input_db,))

        cur = src_conn.cursor()
        cur.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        )
        table_names = [row[0] for row in cur.fetchall()]

        for table_name in table_names:
            print("  - {}".format(table_name))
            copy_table_data(src_conn, dst_conn, table_name, start_frame, end_frame, start_ts, end_ts)

        dst_conn.commit()

        dst_conn.execute("DETACH DATABASE main_src")
        dst_conn.commit()

    finally:
        src_conn.close()
        dst_conn.close()

    return final_output_db


def main():
    args = parse_args()

    input_db = args.input
    output_db = args.output

    if input_db is None:
        input_db = choose_input_database(initial_path=os.getcwd())
        if input_db is None:
            raise ValueError("No input database selected")

    if output_db is None:
        output_db = choose_output_database(initial_path=os.path.dirname(input_db))
        if output_db is None:
            raise ValueError("No output database selected")

    start_frame = args.start_frame
    end_frame = args.end_frame
    start_ts = None
    end_ts = None

    src_conn = sqlite3.connect(input_db)
    try:
        has_time_args = (
            args.start_frame is not None
            or args.end_frame is not None
            or args.start_time is not None
            or args.end_time is not None
        )

        if has_time_args:
            validate_time_selection(args)

            if args.start_time is not None and args.end_time is not None:
                start_ts = datetime_to_epoch_ms(args.start_time)
                end_ts = datetime_to_epoch_ms(args.end_time)
                start_frame, end_frame = get_frame_bounds_from_time(src_conn, args.start_time, args.end_time)
            else:
                start_frame = args.start_frame
                end_frame = args.end_frame
        else:
            start_frame, end_frame, start_ts, end_ts = choose_time_window_interactive(src_conn)

        if end_frame < start_frame:
            raise ValueError("end-frame must be >= start-frame")

    finally:
        src_conn.close()

    final_output_path = copy_selected_period(
        input_db=input_db,
        output_db=output_db,
        start_frame=start_frame,
        end_frame=end_frame,
        start_ts=start_ts,
        end_ts=end_ts,
    )

    print("Done.")
    print("Input : {}".format(input_db))
    print("Output: {}".format(final_output_path))
    print("Copied frame window: {} -> {}".format(start_frame, end_frame))


if __name__ == "__main__":
    main()
