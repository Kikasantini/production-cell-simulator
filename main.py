import json
import csv
import time
import uuid
from datetime import datetime
from pathlib import Path
from enum import Enum

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
max_consecutive_missed_signals = int(config["max_consecutive_missed_signals"])

# Config data validation:
if target_quantity <= 0:
    raise ValueError(f"target_quantity ({target_quantity}) must be greater than zero.")
if signal_interval_seconds <= 0:
    raise ValueError(f"signal_interval_seconds ({signal_interval_seconds}) must be greater than zero.")
if max_signal_attempts < target_quantity:
    raise ValueError(f"max_signal_attempts ({max_signal_attempts}) must be at least target_quantity ({target_quantity}).")
if max_consecutive_missed_signals <= 0:
    raise ValueError("max_consecutive_missed_signals must be greater than zero.")

class CellState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    INCOMPLETE = "incomplete"
    FAULT = "fault"


# Signal generation simulator
def simulate_sensor_signal(signal_number, missed_signal_numbers):
    if signal_number in missed_signal_numbers:
        print(f"Sensor signal {signal_number}: no piece detected")
        return False
    print(f"Sensor signal {signal_number}: piece detected")
    return True


# Log writer
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


def run_production(
        work_order_id,
        target_quantity,
        max_signal_attempts,
        signal_interval_seconds,
        missed_signal_numbers,
        max_consecutive_missed_signals
):
    piece_count = 0
    consecutive_missed_signals = 0
    cell_state = CellState.IDLE

    cell_state = CellState.RUNNING
    for signal_number in range(1, max_signal_attempts + 1):
        time.sleep(signal_interval_seconds)
        piece_detected = simulate_sensor_signal(signal_number, missed_signal_numbers)
        if piece_detected:
            consecutive_missed_signals = 0
            piece_count += 1
            write_log("piece_detected", piece_count)
            print(f"Current count: {piece_count}/{target_quantity}")

            if piece_count == target_quantity:
                cell_state = CellState.COMPLETED
                print(f"\nTarget reached for work order {work_order_id}.")
                print(f"Automatic action: record production.")
                write_log("production_recorded", piece_count)
                break
        else:
            write_log("no_piece_detected", piece_count)
            consecutive_missed_signals += 1
            print(f"Consecutive missed signals: {consecutive_missed_signals}/{max_consecutive_missed_signals}")

            if consecutive_missed_signals >= max_consecutive_missed_signals:
                cell_state = CellState.FAULT
                print("\nSensor fault: maximum consecutive missed signals reached.")
                write_log("sensor_fault", piece_count)
                break
    
    if piece_count < target_quantity and cell_state != CellState.FAULT:
        cell_state = CellState.INCOMPLETE
        print(f"Work order incomplete: produced {piece_count}/{target_quantity} pieces after {max_signal_attempts} signal attempts.")  
        write_log("order_incomplete", piece_count)

    return cell_state, piece_count


# Main
def main():
    print(f"Machine: {machine_name}")
    print(f"Work order: {work_order_id}")
    print(f"Target quantity: {target_quantity} pieces")
    print("\nSimulating sensor signals...\n")

    cell_state, piece_count = run_production(
        work_order_id=work_order_id,
        target_quantity=target_quantity,
        max_signal_attempts=max_signal_attempts,
        signal_interval_seconds=signal_interval_seconds,
        missed_signal_numbers=config["missed_signal_numbers"],
        max_consecutive_missed_signals=max_consecutive_missed_signals,
    )

    print(f"\nCell state: {cell_state.value}")
    print(f"\nEvent log saved to: {log_path.name}")


if __name__ == "__main__":
    main()