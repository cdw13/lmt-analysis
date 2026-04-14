'''
018_time_spent_in_area_identified_and_inferred

Compute, for each mouse:
- identified time spent in a given area
- inferred time spent in the area during identity-loss gaps
  (when the mouse was last identified in the area and at least one anonymous
   detection is present in the area on missing frames)

created by GitHub Copilot, 2026-03-30
'''

import csv
import sqlite3
import os
from datetime import datetime

from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Measure import oneHour


# ----------------------------- USER PARAMETERS -----------------------------
START = 0
END = 22 * oneHour
FPS = 30.0

# Area is expressed in cm from top-left corner of open field.
AREA_X_MIN = 0.0
AREA_X_MAX = 25.0
AREA_Y_MIN = 0.0
AREA_Y_MAX = 25.0
# -------------------------------------------------------------------------


def is_detection_in_area(detection, parameters):
    x_cm = (detection.massX - parameters.cornerCoordinatesOpenFieldArea[0][0]) * parameters.scaleFactor
    y_cm = (detection.massY - parameters.cornerCoordinatesOpenFieldArea[0][1]) * parameters.scaleFactor

    return (AREA_X_MIN <= x_cm <= AREA_X_MAX) and (AREA_Y_MIN <= y_cm <= AREA_Y_MAX)


def get_anonymous_in_area_frames(animal_pool, parameters):
    anonymous_in_area = {}

    for frame, detection_list in animal_pool.anonymousDetection.items():
        frame_has_anon_in_area = False
        for detection in detection_list:
            if is_detection_in_area(detection, parameters):
                frame_has_anon_in_area = True
                break

        anonymous_in_area[frame] = frame_has_anon_in_area

    return anonymous_in_area


def compute_time_in_area_for_animal(animal, parameters, anonymous_in_area_frames):
    key_list = sorted(animal.detectionDictionary.keys())

    identified_in_area_frames = 0
    inferred_in_area_frames = 0

    # Count identified frames in area.
    in_area_by_frame = {}
    for frame in key_list:
        detection = animal.detectionDictionary.get(frame)
        in_area = is_detection_in_area(detection, parameters)
        in_area_by_frame[frame] = in_area

        if in_area:
            identified_in_area_frames += 1

    # Infer anonymous-in-area frames during identity gaps.
    for i in range(1, len(key_list)):
        previous_frame = key_list[i - 1]
        current_frame = key_list[i]
        gap = current_frame - previous_frame

        if gap <= 1:
            continue

        # Mouse became anonymous after being seen in area.
        if not in_area_by_frame.get(previous_frame, False):
            continue

        for missing_frame in range(previous_frame + 1, current_frame):
            if anonymous_in_area_frames.get(missing_frame, False):
                inferred_in_area_frames += 1

    identified_sec = identified_in_area_frames / FPS
    inferred_sec = inferred_in_area_frames / FPS

    return {
        'identified_in_area_frames': identified_in_area_frames,
        'identified_in_area_sec': identified_sec,
        'inferred_anonymous_in_area_frames': inferred_in_area_frames,
        'inferred_anonymous_in_area_sec': inferred_sec,
        'estimated_total_in_area_frames': identified_in_area_frames + inferred_in_area_frames,
        'estimated_total_in_area_sec': identified_sec + inferred_sec,
    }


if __name__ == '__main__':

    files = getFilesToProcess()

    if not files:
        print('No file selected. Exiting.')
        raise SystemExit(0)

    first_filename = os.path.splitext(os.path.basename(files[0]))[0]
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_filename = f'time_in_area_identified_and_inferred-{first_filename}-{now}.csv'

    with open(output_filename, 'w', newline='') as out_csv:
        writer = csv.writer(out_csv)
        writer.writerow([
            'file',
            'mouse_id',
            'rfid',
            'name',
            'area_x_min_cm',
            'area_x_max_cm',
            'area_y_min_cm',
            'area_y_max_cm',
            'start_frame',
            'end_frame',
            'identified_in_area_frames',
            'identified_in_area_sec',
            'inferred_anonymous_in_area_frames',
            'inferred_anonymous_in_area_sec',
            'estimated_total_in_area_frames',
            'estimated_total_in_area_sec',
            'inference_rule'
        ])

        for file in files:
            print(file)

            connection = sqlite3.connect(file)
            animal_pool = AnimalPool()
            animal_pool.loadAnimals(connection)

            # lightLoad=True is enough for area-based calculations (massX, massY)
            animal_pool.loadDetection(start=START, end=END, lightLoad=True)
            animal_pool.loadAnonymousDetection(start=START, end=END)

            animal_list = animal_pool.getAnimalList()
            if len(animal_list) == 0:
                print('No animals found in file.')
                connection.close()
                continue

            # Parameters are shared by animals in same experiment.
            parameters = animal_list[0].parameters
            anonymous_in_area_frames = get_anonymous_in_area_frames(animal_pool, parameters)

            print('Area (cm):', AREA_X_MIN, AREA_X_MAX, AREA_Y_MIN, AREA_Y_MAX)

            for animal in animal_list:
                result = compute_time_in_area_for_animal(animal, parameters, anonymous_in_area_frames)

                print(
                    f"Animal RFID={animal.RFID} "
                    f"identified={result['identified_in_area_sec']:.2f}s "
                    f"inferred={result['inferred_anonymous_in_area_sec']:.2f}s "
                    f"total={result['estimated_total_in_area_sec']:.2f}s"
                )

                writer.writerow([
                    file,
                    animal.baseId,
                    animal.RFID,
                    animal.name,
                    AREA_X_MIN,
                    AREA_X_MAX,
                    AREA_Y_MIN,
                    AREA_Y_MAX,
                    START,
                    END,
                    result['identified_in_area_frames'],
                    result['identified_in_area_sec'],
                    result['inferred_anonymous_in_area_frames'],
                    result['inferred_anonymous_in_area_sec'],
                    result['estimated_total_in_area_frames'],
                    result['estimated_total_in_area_sec'],
                    'Count missing frames between two identified detections when previous identified frame is in area and anonymous detection exists in area'
                ])

            connection.close()

    print(f'Output saved to: {output_filename}')
