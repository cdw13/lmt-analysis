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

    cur.execute("SELECT ID, NAME, RFID FROM ANIMAL ORDER BY ID")
    animals = cur.fetchall()

    cur.execute("SELECT STARTFRAME, ENDFRAME FROM EVENT WHERE NAME='Nest4_'")
    nest4 = cur.fetchall()

    cur.execute("SELECT IDANIMALA, STARTFRAME, ENDFRAME FROM EVENT WHERE NAME='Nest3_'")
    nest3 = cur.fetchall()

    cur.execute("SELECT COUNT(*) FROM EVENT WHERE NAME='Nest3_Anonymous'")
    nest3_anon_count = cur.fetchone()[0]

    print(f"Nest3_Anonymous events in DB: {nest3_anon_count}")
    print("ID|NAME|RFID|frames_in_nest_or_group|seconds_at_30fps")

    for aid, name, rfid in animals:
        intervals = []

        # Nest4: mouse considered part of nest/group while Nest4 is active
        intervals.extend(nest4)

        # Nest3: mouse considered part of nest/group when another mouse is singleton
        intervals.extend((s, e) for singleton_id, s, e in nest3 if singleton_id != aid)

        merged = merge_intervals(intervals)
        frames = sum(e - s + 1 for s, e in merged)
        seconds = frames / 30.0

        print(f"{aid}|{name}|{rfid}|{frames}|{seconds:.2f}")

    conn.close()


if __name__ == "__main__":
    main()
