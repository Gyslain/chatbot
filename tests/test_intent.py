import unittest

from helpers.luis_helper import Entities, Intent


class Test_Helpers(unittest.TestCase):
    def test_Intent(self):
        self.assertEqual(Intent.BOOK_FLIGHT.value, "BookFlight")

    def test_Entities(self):
        self.assertEqual(Entities.TO_CITY.value, "dst_city")
        self.assertEqual(Entities.FROM_CITY.value, "or_city")
        self.assertEqual(Entities.BUDGET.value, "budget")
        self.assertEqual(Entities.START_DATE.value, "str_date")
        self.assertEqual(Entities.END_DATE.value, "end_date")
