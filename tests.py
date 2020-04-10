import unittest

from resources.settings import test_data
from helper_functions import load_data, find_nearest

class TestLoadData(unittest.TestCase):
    def setUp(self):
        self.data = test_data

    def test_load(self):
        data = load_data('resources/test_data.csv')
        self.assertEqual(self.data, data)


class TestFindNearest(unittest.TestCase):
    def setUp(self):
        self.xpoints = list(range(11))
        self.array = [0,1,2,3,4,5,4,3,2,1,0]
        self.value = 2
        self.left = 2
        self.middle = 5
        self.right = 8


    def test_find_nearest(self):
        left, middle, right = find_nearest(self.xpoints, self.array, self.value)
        self.assertEqual(left, self.left)
        self.assertEqual(middle, self.middle)
        self.assertEqual(right, self.right)

if __name__ == '__main__':
    unittest.main()