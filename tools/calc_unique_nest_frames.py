#!/usr/bin/env python3
import sqlite3


def merge_intervals(intervals):
    if not intervals:
        return []
    intervals = sorted(intervals)
    merged = [intervals[0]]
    for s, e in intervals[1:]:
        ms, me = merged[-1]
        if s <= me + 1:
            merged[-1] = (ms, max(me, e))
        else:
            merged.append((s, e))
    return merged


def main():
    db = "dc_12022026_pilot_multiple_mice_cw.sqlite"
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT STARTFRAME, ENDFRAME
        FROM EVENT
        WHERE NAME IN ('Nest3_', 'Nest4_')
        """
    )
    intervals = cur.fetchall()

    merged = merge_intervals(intervals)
    unique_frames = sum(e - s + 1 for s, e in merged)

    cur.execute("SELECT COUNT(*) FROM EVENT WHERE NAME='Nest3_'")
    nest3_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM EVENT WHERE NAME='Nest4_'")
    nest4_count = cur.fetchone()[0]

    print(f"Nest3_ events: {nest3_count}")
    print(f"Nest4_ events: {nest4_count}")
    print(f"Merged non-duplicate intervals: {len(merged)}")
    print(f"Total unique frames (Nest3_ OR Nest4_): {unique_frames}")
    print(f"Total unique seconds at 30 fps: {unique_frames / 30:.2f}")

    conn.close()


if __name__ == "__main__":
    main()
