import unittest
import json
import datetime
from traffic_model.simulation.model import Traffic

class MyTestCase(unittest.TestCase):
    def test_path_json(self):
        check_case = 1
        try:
            with open('data/lanesetporc.json') as json_file:
                data = json.load(json_file)
        except:
            case_result = 0
        else:
            case_result = 1
        self.assertEqual(check_case, case_result, "Pathing failed, json path does not exist")
    def test_path_csv(self):
        test_instance = Traffic()
        check_case = 1
        try:
            test_pathing = test_instance.load_data(path='data/BOS210.csv')
        except:
            case_result_2 = 0
        else:
            case_result_2 = 1
        self.assertEqual(check_case, case_result_2, "Pathing failed, csv path does not exist")
    def test_row_reading(self):
        test_instance = Traffic()
        p1 = test_instance.read_row_col('time')
        p2 = '02-11-2020 08:00:00.0'
        #Omdat onze eigen eerste entry om 8 uur is zou dit het resultaat moeten zijn
        self.assertEqual(p1,p2)



if __name__ == '__main__':
    unittest.main()
