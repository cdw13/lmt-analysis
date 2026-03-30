'''
016_find_anonymous_detection_sequences
created by GitHub Copilot, 2026-03-22
'''

import csv
import os
from datetime import datetime
from lmtanalysis.FileUtil import getCsvFileToProcess


def load_frame_counts(csv_file):
    frame_counts = []

    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            frame = int(row['frame'])
            count = int(row['anonymous_detections'])
            frame_counts.append((frame, count))

    frame_counts.sort(key=lambda x: x[0])
    return frame_counts


def get_consecutive_sequences(frame_counts):
    if len(frame_counts) == 0:
        return []

    frames = [frame for frame, _ in frame_counts]

    sequences = []
    start = frames[0]
    previous = frames[0]

    for frame in frames[1:]:
        if frame == previous + 1:
            previous = frame
            continue

        sequences.append((start, previous))
        start = frame
        previous = frame

    sequences.append((start, previous))
    return sequences


def get_1_2_switch_pairs(frame_counts):
    switch_pairs = []

    for i in range(1, len(frame_counts)):
        previous_frame, previous_count = frame_counts[i - 1]
        frame, count = frame_counts[i]

        # only consider true frame-to-frame transitions
        if frame != previous_frame + 1:
            continue

        # keep only 1<->2 transitions
        if previous_count in (1, 2) and count in (1, 2) and previous_count != count:
            switch_pairs.append((previous_frame, frame))

    return switch_pairs


if __name__ == '__main__':

    csv_file = getCsvFileToProcess()

    if not csv_file:
        print('No CSV selected. Exiting.')
        raise SystemExit(0)

    frame_counts = load_frame_counts(csv_file)

    if len(frame_counts) == 0:
        print('CSV has no data rows. Exiting.')
        raise SystemExit(0)

    sequences = get_consecutive_sequences(frame_counts)
    switch_pairs = get_1_2_switch_pairs(frame_counts)

    base_name = os.path.splitext(os.path.basename(csv_file))[0]
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_filename = f'anonymous_detection_sequences-{base_name}-{now}.txt'
    sequences_csv_filename = f'anonymous_detection_sequences-{base_name}-{now}.csv'
    switches_csv_filename = f'anonymous_detection_switches_1_2-{base_name}-{now}.csv'

    with open(output_filename, 'w') as out:
        out.write('Consecutive frame sequences (first_frame, last_frame):\n')
        for sequence in sequences:
            out.write(f'{sequence}\n')

        out.write('\nSwitches between 1 and 2 detections (previous_frame, current_frame):\n')
        for pair in switch_pairs:
            out.write(f'{pair}\n')

    with open(sequences_csv_filename, 'w', newline='') as out_csv:
        writer = csv.writer(out_csv)
        writer.writerow(['first_frame', 'last_frame'])
        for first_frame, last_frame in sequences:
            writer.writerow([first_frame, last_frame])

    with open(switches_csv_filename, 'w', newline='') as out_csv:
        writer = csv.writer(out_csv)
        writer.writerow(['previous_frame', 'current_frame'])
        for previous_frame, current_frame in switch_pairs:
            writer.writerow([previous_frame, current_frame])

    print(f'Loaded {len(frame_counts)} rows from: {csv_file}')
    print(f'Found {len(sequences)} consecutive sequences.')
    print(f'Found {len(switch_pairs)} switches between 1 and 2 detections.')
    print(f'Output saved to: {output_filename}')
    print(f'Sequences CSV saved to: {sequences_csv_filename}')
    print(f'Switches CSV saved to: {switches_csv_filename}')
