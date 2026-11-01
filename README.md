# Production Cell Simulator
A small Python project that simulates sensor signals from a production cell, tracks pieces against a work order target, and records events in a CSV log.

## Features
- Work order, target quantity, signal interval, and maximum attempts are configurable.
- Sensor signals can simulate detected and missed pieces.
- The simulator counts detected pieces and stops when the target is reached.
- Events are recorded in a CSV log with timestamps and a unique run ID.

## Configuration
- `machine_name`: cell name shown in the terminal and log.
- `work_order_id`: work order identifier.
- `target_quantity`: quantity of pieces to be produced for the work order.
- `signal_interval_seconds`: pause between the simulated signals.
- `max_signal_attempts`: maximum number of signals the simulator can generate.
- `missed_signal_numbers`: specific signals where no piece will be detected.
- `max_consecutive_missed_signals`: number of consecutive missed signals allowed before the simulator stops with a sensor fault.

## Running the Simulator
This project uses only Python's standard library, so no additional packages are required.

Run `python main.py` from the project root.

The simulator creates `production_log_with_run_id.csv` in the project root.

## Scope
All sensor events are simulated. This project does not connect to physical sensors, robots, PLCs, or production equipment.