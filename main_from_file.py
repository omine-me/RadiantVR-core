import csv
import time

import argparse
import asyncio

from utils.dmxout import out
from config import config

# column index
Trial_No = 0
Bulb_No = 1
Start_Time = 2
Duration = 3
Intensity = 4

BULB_COUNT = len(config["lights"])
MAX_INTENSITY = 255


def main(file_path):
    with open(file_path, "r") as f:
        # column names
        header = next(csv.reader(f))

        trials = csv.reader(f)
        for trial in trials:
            try:
                bulbs = [int(b) for b in trial[Bulb_No].split(",")]
            except ValueError:
                raise ValueError(f"bulb_no: {trial[Bulb_No]} of trial {trial[Trial_No]} should be integer")
            for bulb in bulbs:
                assert 0 <= bulb < BULB_COUNT, f"bulb_no: {bulb} of trial {trial[Trial_No]} should be in range 0-{BULB_COUNT-1}"
            try:
                start_times = [int(st) for st in trial[Start_Time].split(",")]
            except ValueError:
                raise ValueError(f"start_time: {trial[Start_Time]} of trial {trial[Trial_No]} should be integer")
            for start_time in start_times:
                assert 0 <= start_time, f"start_time: {start_time} of trial {trial[Trial_No]} should be 0 or positive number"
            try:
                durations = [int(d) for d in trial[Duration].split(",")]
            except ValueError:
                raise ValueError(f"duration: {trial[Duration]} of trial {trial[Trial_No]} should be integer")
            for duration in durations:
                assert duration > 0, f"duration: {duration} of trial {trial[Trial_No]} should be positive number"
            try:
                intensities = [int(i) for i in trial[Intensity].split(",")]
            except ValueError:
                raise ValueError(f"intensity: {trial[Intensity]} of trial {trial[Trial_No]} should be integer")
            for intensity in intensities:
                assert 0 <= intensity <= 100, f"intensity: {intensity} of trial {trial[Trial_No]} should be in range 0-100"
            assert len(bulbs) == len(start_times) == len(durations) == len(intensities), f"bulb_no, start_time, duration, and intensity should have the same length in trial {trial[Trial_No]}"
            out_intensities = [0] * BULB_COUNT

            end_time = max([st + d for st, d in zip(start_times, durations)])
            print(f"trail {trial[Trial_No]} ends in {end_time}")

            trial_start_time = int(time.time() * 1000) 
            for ms in range(0, end_time+1, 100):
                st = int(time.time() * 1000)
                is_changed = False
                for bulb, start_time, duration, intensity in zip(bulbs, start_times, durations, intensities):
                    if start_time <= ms < start_time + duration:
                        if out_intensities[bulb] == 0:
                            is_changed = True
                            out_intensities[bulb] = int(MAX_INTENSITY * float(intensity)/100)
                            print(f"    bulb {bulb} is turned on with intensity {out_intensities[bulb]} at {ms} ms")
                    else:
                        if out_intensities[bulb] != 0:
                            is_changed = True
                            out_intensities[bulb] = 0
                            print(f"    bulb {bulb} is turned off at {ms} ms")
                if is_changed:
                    asyncio.run(out(out_intensities))
                if ms == end_time:
                    break
                elapsed_time = (int(time.time() * 1000)) - st
                if elapsed_time < 100:
                    time.sleep(0.1-(max(0, elapsed_time)/1000))
                    # print(f"elapsed_time: {elapsed_time}", "sleep_time: ", 0.1-(elapsed_time/1000))
                else:
                    print(f"{elapsed_time - 100} ms is delayed")
            print(f"trial {trial[Trial_No]} is done in {int(time.time() * 1000) - trial_start_time} ms")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file",
        type=str, required=True, help="csv file path to be read")
    args = parser.parse_args()

    main(args.file)
