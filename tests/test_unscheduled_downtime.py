try:
    from unittest import mock
except ImportError:
    import mock
import unittest
import lsst.utils.tests

from lsst.sims.downtimeModel import UnscheduledDowntime


class UnscheduledDowntimeTest(unittest.TestCase):

    def setUp(self):
        self.usdt = UnscheduledDowntime()

    def check_downtime(self, downtime, night, duration, activity):
        self.assertEqual(downtime[0], night)
        self.assertEqual(downtime[1], duration)
        self.assertEqual(downtime[2], activity)

    def test_basic_information_after_creation(self):
        self.assertEqual(self.usdt.seed, 1516231121)
        self.assertEqual(len(self.usdt), 0)

    def test_information_after_initialization(self):
        self.usdt.initialize()
        self.assertEqual(len(self.usdt), 133)
        self.assertEqual(self.usdt.total_downtime, 315)
        self.check_downtime(self.usdt.downtimes[0], 48, 3, "intermediate event")
        self.check_downtime(self.usdt.downtimes[-1], 7270, 3, "intermediate event")

    @mock.patch("time.time")
    def test_alternate_seed(self, mock_time):
        mock_time.return_value = 1466094470
        self.usdt.initialize(use_random_seed=True)
        self.assertEqual(len(self.usdt), 152)
        self.assertEqual(self.usdt.total_downtime, 325)
        self.check_downtime(self.usdt.downtimes[0], 150, 3, "intermediate event")
        self.check_downtime(self.usdt.downtimes[-1], 7246, 1, "minor event")

    def test_alternate_seed_with_override(self):
        self.usdt.initialize(use_random_seed=True, random_seed=1466094470)
        self.assertEqual(len(self.usdt), 152)
        self.assertEqual(self.usdt.total_downtime, 325)
        self.check_downtime(self.usdt.downtimes[0], 150, 3, "intermediate event")
        self.check_downtime(self.usdt.downtimes[-1], 7246, 1, "minor event")

    def test_call(self):
        self.usdt.initialize()
        self.check_downtime(self.usdt(), 48, 3, "intermediate event")
        self.assertEqual(len(self.usdt), 132)


class TestMemory(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
