import json
import csv
import time
import uuid
from datetime import datetime
from pathlib import Path

config_path = Path(__file__).parent / "config.json"
log_path = Path(__file__).parent / "production_log_with_run_id.csv"

log_fields = [
    "run_id",
    "timestamp",
    "event_type",
    "machine_name",
    "work_order_id",
    "piece_count",
]

with config_path.open(encoding="utf-8") as config_file:
    config = json.load(config_file)

machine_name = config["machine_name"]
work_order_id = config["work_order_id"]
target_quantity = int(config["target_quantity"])
signal_interval_seconds = float(config["signal_interval_seconds"])
run_id = str(uuid.uuid4())
max_signal_attempts = int(config["max_signal_attempts"])

# Data validation:
if target_quantity <= 0:
    raise ValueError(f"target_quantity ({target_quantity}) must be greater than zero.")
if signal_interval_seconds <= 0:
    raise ValueError(f"signal_interval_seconds ({signal_interval_seconds}) must be greater than zero.")
if max_signal_attempts < target_quantity:
    raise ValueError(f"max_signal_attempts ({max_signal_attempts}) must be at least target_quantity ({target_quantity})")


# Signal generation simulator
def simulate_sensor_signal(signal_number, missed_signal_numbers):
    if signal_number in missed_signal_numbers:
        print(f"Sensor signal {signal_number}: no piece detected")
        return False
    print(f"Sensor signal {signal_number}: piece detected")
    return True


def write_log(event_type, piece_count):
    log_exists = log_path.exists()

    with log_path.open("a", newline="", encoding="utf-8") as log_file:
        log_writer = csv.DictWriter(log_file, fieldnames=log_fields)

        if not log_exists:
            log_writer.writeheader()

        log_writer.writerow({
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(timespec="milliseconds"),
            "event_type": event_type,
            "machine_name": machine_name,
            "work_order_id": work_order_id,
            "piece_count": piece_count,
        })

piece_count = 0

print(f"Machine: {machine_name}")
print(f"Work order: {work_order_id}")
print(f"Target quantity: {target_quantity} pieces")
print(f"\nSimulating sensor signals...\n")

for signal_number in range(1, max_signal_attempts + 1):
    time.sleep(signal_interval_seconds)
    piece_detected = simulate_sensor_signal(signal_number, config["missed_signal_numbers"])
    if piece_detected:
        piece_count += 1
        write_log("piece_detected", piece_count)
        print(f"Current count: {piece_count}/{target_quantity}")

        if piece_count == target_quantity:
            print(f"\nTarget reached for work order {work_order_id}.")
            print(f"Automatic action: record production.")
            write_log("production_recorded", piece_count)
            break
    else:
        write_log("no_piece_detected", piece_count)

if piece_count < target_quantity:
    print(f"Work order incomplete: produced {piece_count}/{target_quantity} pieces after {max_signal_attempts} signal attempts.")  
    write_log("order_incomplete", piece_count)

print(f"\nEvent log saved to: {log_path.name}")

