'''
017_find_Identified_time_in_nest
Finds the first interval where an identified mouse enters a given zone,
then loses identity while still in that zone.

created by Caroline Woodard, 2026-03-28
updated by GitHub Copilot, 2026-03-30
'''

import csv
import os
from datetime import datetime
from datetime import timedelta
from lmtanalysis.FileUtil import getCsvFileToProcess


# ----------------------------- USER PARAMETERS -----------------------------
# If None, a file picker dialog is shown.
CSV_FILE = None

# Mouse to track in the detection table.
TARGET_IDENTIFIER = 'B_001040951715'
IDENTIFIER_COLUMN = 'RFID'  # or 'name'

# Zone definition:
# - If True, use a boolean column already present in the table (e.g. in_arena_center).
# - If False, use rectangle bounds with X/Y columns.
USE_ZONE_COLUMN = True
ZONE_COLUMN = 'in_arena_center'

X_COLUMN = 'x_cm'
Y_COLUMN = 'y_cm'
ZONE_X_MIN = 0.0
ZONE_X_MAX = 25.0
ZONE_Y_MIN = 0.0
ZONE_Y_MAX = 25.0

FPS = 30.0
# -------------------------------------------------------------------------


def parse_bool(value):
    return str(value).strip().lower() in ('true', '1', 'yes', 'y')


def load_detection_rows(csv_file):
    rows = []

    with open(csv_file, mode='r', encoding='utf-8', newline='') as f:
        data_lines = [line for line in f if not line.startswith('#') and line.strip()]

    reader = csv.DictReader(data_lines, delimiter='\t')
    for row in reader:
        if row is None:
            continue
        if 'frame' not in row:
            continue

        try:
            row['frame'] = int(row['frame'])
            row['sec'] = float(row['sec']) if 'sec' in row and row['sec'] not in (None, '') else None
        except ValueError:
            continue

        rows.append(row)

    rows.sort(key=lambda r: r['frame'])
    return rows


def is_in_zone(row):
    if USE_ZONE_COLUMN:
        if ZONE_COLUMN not in row:
            raise KeyError(f"Zone column '{ZONE_COLUMN}' not found in file.")
        return parse_bool(row[ZONE_COLUMN])

    if X_COLUMN not in row or Y_COLUMN not in row:
        raise KeyError(f"Columns '{X_COLUMN}'/'{Y_COLUMN}' not found in file.")

    x = float(row[X_COLUMN])
    y = float(row[Y_COLUMN])
    return (ZONE_X_MIN <= x <= ZONE_X_MAX) and (ZONE_Y_MIN <= y <= ZONE_Y_MAX)


def find_first_entry_then_identity_loss(target_rows):
    if len(target_rows) == 0:
        return None

    current_entry_row = None
    prev_row = None
    prev_in_zone = False

    for row in target_rows:
        frame = row['frame']
        in_zone = is_in_zone(row)

        if prev_row is not None:
            prev_frame = prev_row['frame']
            gap = frame - prev_frame

            # Identity loss starts as soon as frame continuity breaks.
            if gap > 1 and prev_in_zone and current_entry_row is not None:
                return {
                    'entry_row': current_entry_row,
                    'last_identified_row': prev_row,
                    'identity_lost_frame': prev_frame + 1
                }

        if in_zone:
            starts_new_zone_visit = (
                (prev_row is None)
                or (not prev_in_zone)
                or (row['frame'] - prev_row['frame'] > 1)
            )
            if starts_new_zone_visit:
                current_entry_row = row
        else:
            current_entry_row = None

        prev_row = row
        prev_in_zone = in_zone

    return None


def format_seconds(value):
    if value is None:
        return 'NA'
    return f"{value:.3f} s ({timedelta(seconds=value)})"


def export_result_to_csv(input_csv_file, result, duration):
    base_name = os.path.splitext(os.path.basename(input_csv_file))[0]
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_csv = f"identified_time_in_zone-{base_name}-{now}.csv"

    entry_row = result['entry_row']
    last_identified_row = result['last_identified_row']
    lost_frame = result['identity_lost_frame']

    entry_sec = entry_row.get('sec')
    last_identified_sec = last_identified_row.get('sec')
    lost_sec = (last_identified_sec + 1.0 / FPS) if last_identified_sec is not None else None

    with open(output_csv, 'w', newline='', encoding='utf-8') as out:
        writer = csv.DictWriter(
            out,
            fieldnames=[
                'input_file',
                'identifier_column',
                'target_identifier',
                'zone_definition',
                'entry_frame',
                'entry_time',
                'entry_sec',
                'last_identified_frame',
                'last_identified_time',
                'identity_lost_frame',
                'identity_lost_sec',
                'duration_sec'
            ]
        )
        writer.writeheader()
        writer.writerow({
            'input_file': input_csv_file,
            'identifier_column': IDENTIFIER_COLUMN,
            'target_identifier': TARGET_IDENTIFIER,
            'zone_definition': ZONE_COLUMN if USE_ZONE_COLUMN else f"rectangle({ZONE_X_MIN},{ZONE_X_MAX},{ZONE_Y_MIN},{ZONE_Y_MAX})",
            'entry_frame': entry_row['frame'],
            'entry_time': entry_row.get('time', 'NA'),
            'entry_sec': entry_sec,
            'last_identified_frame': last_identified_row['frame'],
            'last_identified_time': last_identified_row.get('time', 'NA'),
            'identity_lost_frame': lost_frame,
            'identity_lost_sec': lost_sec,
            'duration_sec': duration
        })

    return output_csv


if __name__ == '__main__':

    csv_file = CSV_FILE if CSV_FILE else getCsvFileToProcess()

    if not csv_file:
        print('No CSV selected. Exiting.')
        raise SystemExit(0)

    rows = load_detection_rows(csv_file)
    target_rows = [r for r in rows if str(r.get(IDENTIFIER_COLUMN, '')).strip() == TARGET_IDENTIFIER]

    if len(target_rows) == 0:
        print(f"No rows found for {IDENTIFIER_COLUMN}='{TARGET_IDENTIFIER}'.")
        raise SystemExit(0)

    result = find_first_entry_then_identity_loss(target_rows)

    if result is None:
        print('No identity-loss interval found after entering the zone.')
        raise SystemExit(0)

    entry_row = result['entry_row']
    last_identified_row = result['last_identified_row']
    lost_frame = result['identity_lost_frame']

    entry_frame = entry_row['frame']
    entry_sec = entry_row.get('sec')
    last_identified_sec = last_identified_row.get('sec')
    lost_sec = (last_identified_sec + 1.0 / FPS) if last_identified_sec is not None else None

    print('First interval found:')
    print(f"  Mouse: {TARGET_IDENTIFIER} ({IDENTIFIER_COLUMN})")
    print(f"  Zone: {ZONE_COLUMN if USE_ZONE_COLUMN else 'rectangle bounds'}")
    print(f"  Entry frame/time: {entry_frame} / {entry_row.get('time', 'NA')} / {format_seconds(entry_sec)}")
    print(f"  Last identified in zone: frame {last_identified_row['frame']} / {last_identified_row.get('time', 'NA')}")
    print(f"  Identity lost at frame: {lost_frame} / approx {format_seconds(lost_sec)}")

    if entry_sec is not None and lost_sec is not None:
        duration = lost_sec - entry_sec
        print(f"  Duration from zone entry to identity loss: {duration:.3f} s ({timedelta(seconds=duration)})")
    else:
        duration = None

    output_csv = export_result_to_csv(csv_file, result, duration)
    print(f"  Result exported to CSV: {output_csv}")