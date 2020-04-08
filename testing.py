import unittest
import requests
from models.Inmate import Inmate


# before you test, make sure that you are running flask and mongodb on your local machine!
def testFlask(state, first, last, active=True):
    """
    send state code as only two lowercase letters!
    send first and last names as lowercase
    by default, we are only returning active and instate records
    ** If your db returns past records as well as active ones, then you need to set active to False in test call
    """
    state = state.lower()
    first = first.lower()
    last = last.lower()
    req = requests.get("http://localhost:5000/api/search?state="+state+"&last="+last+"&first="+first
                       + ("&active=True" if active else "&active=False"))
    return req.json()


class GeorgiaTest(unittest.TestCase):
    state = "ga"

    # when creating a none test case, look through the corresponding inmate database,
    # and find a query (first name and last name) that returns no prisoners
    # then, fill in the following information to confirm that the query returns no inmates
    def test_none(self):
        data = testFlask(self.state, "xxx", "xxx")
        self.assertEqual([], data)

    # when creating a single test case, look through the corresponding inmate database,
    # and find a query (first name and last name) that returns exactly one prisoner
    # then, fill in the following information to confirm that the query returns the correct information
    def test_single(self):
        data = testFlask(self.state, "chadwick", "fagan")
        testData = {
            "name": {
                "first": "CHADWICK",
                "middle": "DEAN",
                "last": "FAGAN"
            },
            "DOB": {
                "day": None,
                "month": None,
                "year": 1976,
                "estimated": False
            }
        }
        self.assertEqual(Inmate().setByDict(data[0]), Inmate().setByDict(testData))

    # when creating a multi test case, look through the corresponding inmate database,
    # and find a query (first name and last name) that returns more than one prisoner
    # fill in the following information to confirm that the query returns the correct information for the last inmate
    def test_multi(self):
        data = testFlask(self.state, "george", "smith")
        testData = {
            "name": {
                "first": "GEORGE",
                "middle": "ROBERT",
                "last": "SMITH"
            },
            "DOB": {
                "day": None,
                "month": None,
                "year": 1971,
                "estimated": False
            }
        }
        self.assertEqual(Inmate().setByDict(data[-1]), Inmate().setByDict(testData))  # not sure if [-1] is a reliable way to index here

if __name__ == '__main__':
    unittest.main()
