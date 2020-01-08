import numpy as np
from astropy.time import Time, TimeDelta
import unittest
import lsst.utils.tests
from lsst.sims.downtimeModel import DowntimeModel, DowntimeModelConfig
from lsst.sims.downtimeModel import ScheduledDowntimeData, UnscheduledDowntimeData

class TestDowntimeModel(unittest.TestCase):
    def setUp(self):
        # Set config to known values.
        config = DowntimeModelConfig()
        config.efd_columns = ['scheduled_downtimes', 'unscheduled_downtimes']
        config.efd_delta_time = 0
        config.target_columns = ['test_time']
        self.config = config

    def test_configure(self):
        # Configure with defaults.
        downtimeModel = DowntimeModel()
        conf = DowntimeModelConfig()
        self.assertEqual(downtimeModel._config, conf)
        # Test specifying the config.
        downtimeModel = DowntimeModel(self.config)
        self.assertEqual(downtimeModel._config, self.config)
        # Test specifying an incorrect config.
        self.assertRaises(RuntimeError, DowntimeModel, 0.8)

    def test_status(self):
        downtimeModel = DowntimeModel()
        confDict = downtimeModel.config_info()
        expected_keys = ['DowntimeModel_version', 'DowntimeModel_sha', 'efd_columns', 'efd_delta_time',
                         'target_columns']
        for k in expected_keys:
            self.assertTrue(k in confDict.keys())

    def test_efd_requirements(self):
        downtimeModel = DowntimeModel(self.config)
        cols = downtimeModel.efd_requirements[0]
        deltaT = downtimeModel.efd_requirements[1]
        self.assertEqual(self.config.efd_columns, cols)
        self.assertEqual(self.config.efd_delta_time, deltaT)

    def test_targetmap_requirements(self):
        downtimeModel = DowntimeModel(self.config)
        self.assertEqual(downtimeModel.target_requirements, self.config.target_columns)

    def test_call(self):
        # Check the calculation from fwhm_500 to fwhm_eff/fwhm_geom.
        # Use simple effective wavelengths and airmass values.
        downtimeModel = DowntimeModel(self.config)
        t = Time('2022-10-01')
        sched = ScheduledDowntimeData(t)
        sched.read_data()
        unsched = UnscheduledDowntimeData(t)
        unsched.make_data()
        efdData = {'unscheduled_downtimes': unsched(),
                   'scheduled_downtimes': sched()}
        # Set time to within first scheduled downtime.
        t_now = sched.downtime[0]['start'] + TimeDelta(0.5, format='jd')
        targetDict = {'test_time': t_now}
        dt_status = downtimeModel(efdData, targetDict)
        # Expect return dict of : {'status': status, 'end': end_down, 'next': next_sched['start']}
        # Check keys
        for k in ('status', 'end', 'next'):
            self.assertTrue(k in dt_status)
        # downtime status is "True" if system is down.
        self.assertEqual(True, dt_status['status'])
        self.assertEqual(dt_status['end'], sched.downtime[0]['end'])
        self.assertEqual(dt_status['next'], sched.downtime[1]['start'])


class TestMemory(lsst.utils.tests.MemoryTestCase):
    pass

def setup_module(module):
    lsst.utils.tests.init()

if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
