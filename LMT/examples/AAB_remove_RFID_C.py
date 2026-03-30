
'''Mouse C has a faulty RFID tag.
Normally LMT can fix identity errors like this:
Visual detection
RFID detected
Identity inference
Mouse 1
RFID A
A
Mouse 2
RFID B
B
Mouse 3
no RFID
must be C

This works via process of elimination.
But when:
C RFID never works
and A or B temporarily lose RFID
Then LMT sees:
Visual detection
RFID detected
Mouse 1
A or none
Mouse 2
none or B
Mouse 3
none

Now the system cannot reassign identities, so the tracking becomes unreliable.
So goal of the script: 
Loads the LMT SQLite file
Completely removes mouse C
Reconstructs identities for A and B only
Uses process of elimination between A and B
So if:
only A RFID detected → other = B
only B RFID detected → other = A
LOGIC:

positions = visual detections

if RFID A present:
    assign detection closest to RFID reader = A

if RFID B present:
    assign detection closest to RFID reader = B

if only one RFID present:
    second detection = other mouse


CODE:'''

import sqlite3

conn = sqlite3.connect("yourfile.sqlite")

cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

print(cursor.fetchall())

[('ANIMAL',), ('sqlite_sequence',), ('DETECTION',), ('RFIDEVENT',), ('FRAME',), ('EVENT',)]

import sqlite3
import pandas as pd
conn = sqlite3.connect(r"C:\Users\user\Desktop\lmt_pilot_ec_2_data\myfile.sqlite")
animals = pd.read_sql_query("SELECT * FROM ANIMAL", conn)
print(animals)
'''ID          RFID GENOTYPE NAME
0   1  001040953473     None    A
1   2  001040951715     None    B
2   3        RFID_C     None    C
detections = pd.read_sql_query("SELECT * FROM DETECTION LIMIT 5", conn)
print(detections)
  ID  FRAMENUMBER  ANIMALID  MASS_X  MASS_Y  MASS_Z  FRONT_X  FRONT_Y  \
0   1           49         1  363.92  330.41   51.88     -1.0     -1.0   
1   2           50         1  364.07  329.92   54.16     -1.0     -1.0   
2   3           51         1  364.30  329.97   53.20     -1.0     -1.0   
3   4           52         1  364.26  330.06   54.80     -1.0     -1.0   
4   5           53         1  364.69  329.49   53.60     -1.0     -1.0   

   FRONT_Z  BACK_X  BACK_Y  BACK_Z  REARING  LOOK_UP  LOOK_DOWN  \
0     -1.0    -1.0    -1.0    -1.0        0        0          0   
1     -1.0    -1.0    -1.0    -1.0        0        0          0   
2     -1.0    -1.0    -1.0    -1.0        0        0          0   
3     -1.0    -1.0    -1.0    -1.0        0        0          0   
4     -1.0    -1.0    -1.0    -1.0        0        0          0   

                                                DATA  
0  <root><DATA isLookingDown="false" isLookingUp=...  
1  <root><DATA isLookingDown="false" isLookingUp=...  
2  <root><DATA isLookingDown="false" isLookingUp=...  
3  <root><DATA isLookingDown="false" isLookingUp=...  
4  <root><DATA isLookingDown="false" isLookingUp=...'''
import sqlite3
import pandas as pd

# paths
input_db = r"C:\Users\user\Desktop\lmt_pilot_ec_2_data\file.sqlite"
output_db = r"C:\Users\user\Desktop\lmt_pilot_ec_2_data\file_corrected.sqlite"

# connect to original database
conn = sqlite3.connect(input_db)

# load tables
animals = pd.read_sql_query("SELECT * FROM ANIMAL", conn)
detections = pd.read_sql_query("SELECT * FROM DETECTION", conn)
frames = pd.read_sql_query("SELECT * FROM FRAME", conn)
events = pd.read_sql_query("SELECT * FROM EVENT", conn)
rfid = pd.read_sql_query("SELECT * FROM RFIDEVENT", conn)

conn.close()

# remove mouse C
animals = animals[animals["ID"].isin([1,2])]
detections = detections[detections["ANIMALID"].isin([1,2])]

detections = detections.sort_values(["FRAMENUMBER","ANIMALID"])

corrected_rows = []

for frame, group in detections.groupby("FRAMENUMBER"):

    animals_present = set(group["ANIMALID"])

    if animals_present == {1,2}:
        corrected_rows.append(group)

    elif animals_present == {1}:
        row = group.iloc[0].copy()
        row["ANIMALID"] = 2
        corrected_rows.append(group)
        corrected_rows.append(pd.DataFrame([row]))

    elif animals_present == {2}:
        row = group.iloc[0].copy()
        row["ANIMALID"] = 1
        corrected_rows.append(group)
        corrected_rows.append(pd.DataFrame([row]))

corrected_detections = pd.concat(corrected_rows)

# create new sqlite database
conn_new = sqlite3.connect(output_db)

animals.to_sql("ANIMAL", conn_new, index=False, if_exists="replace")
corrected_detections.to_sql("DETECTION", conn_new, index=False, if_exists="replace")
frames.to_sql("FRAME", conn_new, index=False, if_exists="replace")
events.to_sql("EVENT", conn_new, index=False, if_exists="replace")
rfid.to_sql("RFIDEVENT", conn_new, index=False, if_exists="replace")

conn_new.close()

print("New corrected SQLite database created.")

