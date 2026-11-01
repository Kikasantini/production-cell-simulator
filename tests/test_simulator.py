import unittest
from main import simulate_sensor_signal

class TestSimulateSensorSignal(unittest.TestCase):
    
    def test_detected_signal_returns_true(self):
        result = simulate_sensor_signal(1, [])
        self.assertTrue(result)

    def test_missed_signal_returns_false(self):
        result = simulate_sensor_signal(3, [3])
        self.assertFalse(result)

    