import unittest
from tools.XML_tool import *

file = '../../tools/input/79190154_BOS210_ITF_COMPLETE.xml'


class MyTestCases(unittest.TestCase):

    def test_format_lat_lon(self):
        # Tests the format function
        self.assertEqual(format_lat_lon('800', '800'), ('80.0', '8.00'))

    def test_lane_type(self):
        # checks if the retrieved lane types are as expected.
        root = load_data(file)
        generic_lane = root.findall('.//genericLane')

        self.assertEqual(lane_type(generic_lane[0].find('.//laneAttributes')), 'vehicle')
        self.assertEqual(lane_type(generic_lane[2].find('.//laneAttributes')), 'bikeLane')
        self.assertEqual(lane_type(generic_lane[4].find('.//laneAttributes')), 'crosswalk')

    def test_func_sensor_position(self):
        # Checks if the retrieved sensor positions are as expected.
        root = load_data(file)
        intersection = root.find('.//controlledIntersection')
        sensor = intersection.find('sensors')
        position = (sensor[0].find('sensorPosition'))
        self.assertEqual(func_sensor_position(position), ('51.6830938', '5.2943482'))

    def test_func_real_sensor_position(self):
        # Checks if the geoshapes are as expected.
        root = load_data(file)
        intersection = root.find('.//controlledIntersection')
        sensor = intersection.find('sensors')
        geo_shape = (sensor[0].find('geoShape'))
        self.assertEqual(func_real_sensor_position(geo_shape), (('51.6831035', '5.2943401'),
                                                                ('51.6830883', '5.2943692')))

    def test_func_connects_to(self):
        # Checks if the dict is the right format and contains the expected data.
        root = load_data(file)
        generic_lane = root.find('.//genericLane')
        connects_to = generic_lane.find('.//connectsTo')
        signal_dict = {'1': '01', '2': '03', '3': '04', '4': '05', '5': '11',
                       '6': '12', '7': '22', '8': '24', '9': '28', '10': '31',
                       '11': '32', '12': '37', '13': '38', '14': '41'}

        connection = connects_to.find('connection')
        connecting_lane = connection.find('connectingLane')
        lane = connecting_lane.find('lane').text
        maneuver = connecting_lane.find('maneuver').text
        signal_group = signal_dict[connection.find('signalGroup').text]
        connection_id = connection.find('connectionID').text
        connects_to_dict = {'lane': lane, 'maneuver': maneuver, 'signalGroup': signal_group,
                            'connectionID': connection_id}
        self.assertEqual(func_connects_to(connects_to, signal_dict), {'lane': '26',
                                                                      'maneuver': '100000000000',
                                                                      'signalGroup': '11',
                                                                      'connectionID': '1'})

    def test_func_regional(self):
        # Checks if the regional latitudes and longitudes are the right format and the same as we expected.
        root = load_data(file)
        generic_lane = root.find('.//genericLane')
        regional = generic_lane.find('.//regional')
        self.assertEqual(func_regional(regional), [{'pos': ('51.6831190', '5.2938207')},
                                                   {'pos': ('51.6830587', '5.2938612')},
                                                   {'pos': ('51.6829923', '5.2939160')},
                                                   {'pos': ('51.6829464', '5.2939591')},
                                                   {'pos': ('51.6828937', '5.2940163')},
                                                   {'pos': ('51.6828124', '5.2941116')}])


if __name__ == '__main__':
    unittest.main()
