'''
016_find_anonymous_detection_sequences
created by GitHub Copilot, 2026-03-22
'''

import csv
import os
from datetime import datetime
from lmtanalysis.FileUtil import getCsvFileToProcess


# Set to an integer (e.g. 10) to export only the N longest sequences.
# Set to None to export all sequences.
TOP_N_LONGEST = 30


def get_first_existing_key(row, candidate_keys):
    for key in candidate_keys:
        if key in row:
            return key
    return None


def load_frame_counts(csv_file):
    frame_counts = []

    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f)

        first_row = next(reader, None)
        if first_row is None:
            return frame_counts

        frame_key = get_first_existing_key(first_row, ['frame', 'Frame'])
        count_key = get_first_existing_key(first_row, ['anonymous_detections', 'Anonymous_Detections'])

        if frame_key is None or count_key is None:
            raise KeyError(
                "Could not find expected columns. "
                "Accepted frame columns: frame/Frame; "
                "accepted count columns: anonymous_detections/Anonymous_Detections"
            )

        # Process first row then remaining rows.
        rows = [first_row] + list(reader)
        for row in rows:
            frame = int(row[frame_key])
            count = int(row[count_key])
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


def get_sequence_length(sequence):
    start, end = sequence
    return end - start + 1


def get_top_n_longest_sequences(sequences, top_n=None):
    ranked = sorted(
        sequences,
        key=lambda seq: (get_sequence_length(seq), seq[0]),
        reverse=True
    )
    if top_n is None:
        return ranked
    return ranked[:top_n]


def get_switch_pairs(frame_counts):
    switch_pairs = []

    for i in range(1, len(frame_counts)):
        previous_frame, previous_count = frame_counts[i - 1]
        frame, count = frame_counts[i]

        # only consider true frame-to-frame transitions
        if frame != previous_frame + 1:
            continue

        # keep any count switch between consecutive frames
        if previous_count != count:
            switch_pairs.append((previous_frame, frame, previous_count, count))

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
    longest_sequences = get_top_n_longest_sequences(sequences, TOP_N_LONGEST)
    switch_pairs = get_switch_pairs(frame_counts)

    base_name = os.path.splitext(os.path.basename(csv_file))[0]
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_filename = f'016-{base_name}-{now}.txt'
    sequences_csv_filename = f'016-seq{base_name}-{now}.csv'
    longest_sequences_csv_filename = f'016-longest{base_name}-{now}.csv'
    switches_csv_filename = f'016-switches{base_name}-{now}.csv'

    with open(output_filename, 'w') as out:
        out.write('Consecutive frame sequences (first_frame, last_frame):\n')
        for sequence in sequences:
            out.write(f'{sequence}\n')

        out.write('\nLongest sequences (sorted by length desc):\n')
        for sequence in longest_sequences:
            out.write(f'{sequence} length={get_sequence_length(sequence)}\n')

        out.write('\nSwitches in anonymous detection count (previous_frame, current_frame, previous_count, current_count):\n')
        for pair in switch_pairs:
            out.write(f'{pair}\n')

    with open(sequences_csv_filename, 'w', newline='') as out_csv:
        writer = csv.writer(out_csv)
        writer.writerow(['first_frame', 'last_frame', 'length'])
        for first_frame, last_frame in sequences:
            writer.writerow([first_frame, last_frame, get_sequence_length((first_frame, last_frame))])

    with open(longest_sequences_csv_filename, 'w', newline='') as out_csv:
        writer = csv.writer(out_csv)
        writer.writerow(['rank', 'first_frame', 'last_frame', 'length'])
        for i, (first_frame, last_frame) in enumerate(longest_sequences, start=1):
            writer.writerow([i, first_frame, last_frame, get_sequence_length((first_frame, last_frame))])

    with open(switches_csv_filename, 'w', newline='') as out_csv:
        writer = csv.writer(out_csv)
        writer.writerow(['previous_frame', 'current_frame', 'previous_count', 'current_count'])
        for previous_frame, current_frame, previous_count, current_count in switch_pairs:
            writer.writerow([previous_frame, current_frame, previous_count, current_count])

    print(f'Loaded {len(frame_counts)} rows from: {csv_file}')
    print(f'Found {len(sequences)} consecutive sequences.')
    if TOP_N_LONGEST is None:
        print(f'Exported all longest-sequence rankings ({len(longest_sequences)} rows).')
    else:
        print(f'Exported top {len(longest_sequences)} longest sequences (TOP_N_LONGEST={TOP_N_LONGEST}).')
    print(f'Found {len(switch_pairs)} switches in anonymous detection count.')
    print(f'Output saved to: {output_filename}')
    print(f'Sequences CSV saved to: {sequences_csv_filename}')
    print(f'Longest sequences CSV saved to: {longest_sequences_csv_filename}')
    print(f'Switches CSV saved to: {switches_csv_filename}')
