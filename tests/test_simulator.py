import unittest
from unittest.mock import patch
from main import CellState, run_production, simulate_sensor_signal

class TestSimulateSensorSignal(unittest.TestCase):
    
    def test_detected_signal_returns_true(self):
        result = simulate_sensor_signal(1, [])
        self.assertTrue(result)

    def test_missed_signal_returns_false(self):
        result = simulate_sensor_signal(3, [3])
        self.assertFalse(result)

    def test_production_completes_when_target_is_reached(self):
        with patch("main.time.sleep"), patch("main.write_log"):
            cell_state, piece_count = run_production(
                work_order_id="WO_TEST",
                target_quantity=2,
                max_signal_attempts=3,
                signal_interval_seconds=0.1,
                missed_signal_numbers=[],
                max_consecutive_missed_signals=3,
            )
        self.assertEqual(cell_state, CellState.COMPLETED)
        self.assertEqual(piece_count, 2)


    def test_production_is_incomplete_when_attempts_run_out(self):
        with patch("main.time.sleep"), patch("main.write_log"):
            cell_state, piece_count = run_production(
                work_order_id="WO-TEST",
                target_quantity=3,
                max_signal_attempts=3,
                signal_interval_seconds=0.1,
                missed_signal_numbers=[2],
                max_consecutive_missed_signals=3,
            )
        self.assertEqual(cell_state, CellState.INCOMPLETE)
        self.assertEqual(piece_count, 2)

    def test_production_stops_after_consecutive_missed_signals(self):
        with patch("main.time.sleep"), patch("main.write_log"):
            cell_state, piece_count = run_production(
                work_order_id="WO-TEST",
                target_quantity=10,
                max_signal_attempts=5,
                signal_interval_seconds=0.1,
                missed_signal_numbers=[1, 2, 3],
                max_consecutive_missed_signals=3,
            )
        self.assertEqual(cell_state, CellState.FAULT)
        self.assertEqual(piece_count, 0)