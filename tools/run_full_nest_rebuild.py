#!/usr/bin/env python3
import sqlite3

from lmtanalysis import BuildEventNest3, BuildEventNest4
from lmtanalysis.AnimalType import AnimalType


def main():
    file = "dc_12022026_pilot_multiple_mice_cw.sqlite"
    conn = sqlite3.connect(file)
    cur = conn.cursor()
    cur.execute("SELECT MIN(FRAMENUMBER), MAX(FRAMENUMBER) FROM FRAME")
    tmin, tmax = cur.fetchone()
    print("Running nest rebuild on full range:", tmin, tmax)

    BuildEventNest3.reBuildEvent(conn, file, tmin=tmin, tmax=tmax, animalType=AnimalType.MOUSE)
    BuildEventNest4.reBuildEvent(conn, file, tmin=tmin, tmax=tmax, animalType=AnimalType.MOUSE)

    cur.execute("SELECT COUNT(*) FROM EVENT WHERE NAME='Nest3_'")
    print("Nest3_ total events:", cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM EVENT WHERE NAME='Nest3_Anonymous'")
    print("Nest3_Anonymous total events:", cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM EVENT WHERE NAME='Nest4_'")
    print("Nest4_ total events:", cur.fetchone()[0])

    conn.close()
    print("Done")


if __name__ == "__main__":
    main()
