import tools.readjson as tr
import json
import unittest


class TestAgents(unittest.TestCase):
    def test_normalize(self):
        p1 = tr.normalize([8, 4, 3, 2, 7, 6, 5])
        p2 = tr.normalize([1, 2, 2, 3, 3, 3, 4])
        self.assertEqual(p1, [1, 1 / 3, 1 / 6, 0, 5 / 6, 4 / 6, 1 / 2], "Normalisatie is incorrect")
        self.assertEqual(p2, [0, 1 / 3, 1 / 3, 2 / 3, 2 / 3, 2 / 3, 1], "Normalisatie is incorrect")

    def test_convert_time(self):
        p1 = tr.convert_time('2021-01-08T12:18:47Z')
        p2 = '08-01-2021 13:18:47.000000'
        self.assertEqual(p1, p2, "Time conversion is incorrect")

    def test_path(self):
        p1 = 1
        subject_path = 'laneset_BOS210.json'
        try:
            with open(subject_path) as json_file:
                x = json.load(json_file)
        except:
            p2 = 0
        else:
            p2 = 1
        self.assertEqual(p1,p2,"Pathing failed")



if __name__ == '__main__':
    unittest.main()
p1 = tr.convert_time("2021-01-08T12:08:38Z")
print(p1)
