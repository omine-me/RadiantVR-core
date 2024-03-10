import csv
import time

import argparse
import asyncio

from utils.dmxout import out
from config import config

# column index
Trial_No = 0
Bulb_No = 1
Duration = 2
Intensity = 3

BULB_COUNT = len(config["lights"])
MAX_INTENSITY = 255


def main(file_path):
    with open(file_path, "r") as f:
        # column names
        header = next(csv.reader(f))

        trials = csv.reader(f)
        for trial in trials:
            intensities = [0] * BULB_COUNT
            for bulb_no in trial[Bulb_No].split(","):
                assert bulb_no.isdecimal() and 0 <= int(bulb_no) < BULB_COUNT, f"bulb_no: {bulb_no} of trial {trial[Trial_No]} should be in range 0-{BULB_COUNT-1}"
                assert trial[Intensity].isdecimal() and 0 <= int(trial[Intensity]) <= 100, f"intensity: {trial[Intensity]} of trial {trial[Trial_No]} should be in range 0-100"
                intensities[int(bulb_no)] = int(MAX_INTENSITY * float(trial[Intensity])/100)
            asyncio.run(out(intensities))
            print(f"Turning {trial[Bulb_No]} on for {trial[Duration]} ms")
            assert trial[Duration].isdecimal() and float(trial[Duration]) > 0, f"duration: {trial[Duration]} of trial {trial[Trial_No]} should be positive number"
            time.sleep(float(trial[Duration]) / 1000)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file",
        type=str, required=True, help="csv file path to be read")
    args = parser.parse_args()

    main(args.file)
