import os
import sqlite3
import unittest
from astropy.time import Time, TimeDelta
from lsst.utils import getPackageDir
import lsst.utils.tests
from lsst.utils.tests import getTempFilePath

from lsst.sims.downtimeModel import ScheduledDowntimeData


class ScheduledDowntimeDataTest(unittest.TestCase):

    def setUp(self):
        self.th = Time('2020-01-01', format='isot', scale='tai')
        self.startofnight = -0.34
        self.downtime_db = os.path.join(getPackageDir('sims_downtimeModel'), 'data', 'scheduled_downtime.db')

    def test_basic_information_after_creation(self):
        downtimeData = ScheduledDowntimeData(self.th, start_of_night_offset=self.startofnight)
        self.assertEqual(downtimeData.scheduled_downtime_db, self.downtime_db)
        self.assertIsNone(downtimeData.downtime)
        self.assertEqual(self.th + TimeDelta(self.startofnight, format='jd'), downtimeData.night0)
        downtimeData = ScheduledDowntimeData(self.th, start_of_night_offset=0)
        self.assertEqual(downtimeData.night0, self.th)

    def test_information_after_initialization(self):
        downtimeData = ScheduledDowntimeData(self.th, start_of_night_offset=self.startofnight)
        downtimeData.read_data()
        self.assertEqual(len(downtimeData.downtime), 31)
        # Check some of the downtime values.
        dnight = downtimeData.downtime['end'] - downtimeData.downtime['start']
        self.assertEqual(dnight[0].jd, 7)
        self.assertEqual(downtimeData.downtime['activity'][0], 'general maintenance')
        self.assertEqual(dnight[4].jd, 14)
        self.assertEqual(downtimeData.downtime['activity'][4], 'recoat mirror')

    def test_alternate_db(self):
        with getTempFilePath('.alt_downtime.db') as tmpdb:
            downtime_table = []
            downtime_table.append("night INTEGER PRIMARY KEY")
            downtime_table.append("duration INTEGER")
            downtime_table.append("activity TEXT")

            with sqlite3.connect(tmpdb) as conn:
                cur = conn.cursor()
                cur.execute("DROP TABLE IF EXISTS Downtime")
                cur.execute("CREATE TABLE Downtime({})".format(",".join(downtime_table)))
                cur.execute("INSERT INTO Downtime VALUES(?, ?, ?)", (100, 7, "something to do"))
                cur.close()

            downtimeData = ScheduledDowntimeData(self.th,
                                                 scheduled_downtime_db=tmpdb,
                                                 start_of_night_offset = self.startofnight)
            downtimeData.read_data()
            self.assertEqual(len(downtimeData.downtime), 1)
            self.assertEqual(downtimeData.downtime['activity'][0], 'something to do')

    def test_call(self):
        downtimeData = ScheduledDowntimeData(self.th, start_of_night_offset=self.startofnight)
        downtimeData.read_data()
        downtimes = downtimeData()
        self.assertEqual(downtimes['activity'][4], 'recoat mirror')


class TestMemory(lsst.utils.tests.MemoryTestCase):
    pass

def setup_module(module):
    lsst.utils.tests.init()

if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
