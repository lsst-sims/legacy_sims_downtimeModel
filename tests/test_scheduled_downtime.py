import os
import sqlite3
import unittest
import lsst.utils.tests

from lsst.sims.downtimeModel import ScheduledDowntime


class ScheduledDowntimeTest(unittest.TestCase):

    def setUp(self):
        self.sdt = ScheduledDowntime()

    def check_downtime(self, downtime, night, duration, activity):
        self.assertEqual(downtime[0], night)
        self.assertEqual(downtime[1], duration)
        self.assertEqual(downtime[2], activity)

    def test_basic_information_after_creation(self):
        self.assertIsNone(self.sdt.downtime_file)
        self.assertEqual(len(self.sdt), 0)

    def test_information_after_initialization(self):
        self.sdt.initialize()
        self.assertEqual(os.path.basename(self.sdt.downtime_file), "scheduled_downtime.db")
        self.assertEqual(len(self.sdt), 31)
        self.check_downtime(self.sdt.downtimes[0], 158, 7, "general maintenance")
        self.check_downtime(self.sdt.downtimes[-1], 7242, 7, "general maintenance")

    def test_alternate_db(self):
        downtime_dbfile = "alternate_scheduled_downtime.db"

        downtime_table = []
        downtime_table.append("night INTEGER PRIMARY KEY")
        downtime_table.append("duration INTEGER")
        downtime_table.append("activity TEXT")

        with sqlite3.connect(downtime_dbfile) as conn:
            cur = conn.cursor()
            cur.execute("DROP TABLE IF EXISTS Downtime")
            cur.execute("CREATE TABLE Downtime({})".format(",".join(downtime_table)))
            cur.execute("INSERT INTO Downtime VALUES(?, ?, ?)", (100, 7, "something to do"))
            cur.close()

        self.sdt.initialize(downtime_dbfile)
        self.assertEqual(len(self.sdt), 1)
        self.check_downtime(self.sdt.downtimes[0], 100, 7, "something to do")

        os.remove(downtime_dbfile)

    def test_call(self):
        self.sdt.initialize()
        self.check_downtime(self.sdt(), 158, 7, "general maintenance")
        self.assertEqual(len(self.sdt), 30)


class TestMemory(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
