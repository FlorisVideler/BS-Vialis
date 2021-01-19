from xml.etree import ElementTree as ET
import os
dir_path = os.path.dirname(os.path.realpath(__file__))


def load_data():
    tree = ET.parse(dir_path + '/79190154_BOS210_ITF_COMPLETE.xml')
    root = tree.getroot()
    return root


def format_lat_lon(la, lo):
    """
    This function transforms the latitude and longitude into a usuable format
    :param la: int
    :param lo: int
    :return: (float, float)
    """

    la = la[:2] + '.' + la[2:]
    lo = lo[:1] + '.' + lo[1:]
    return la, lo


def lane_type(lane_attributes):
    """
    This function retrieves the lane type.
    :param lane_attributes: string,
    :return: type_lane: string
    """

    type_lane = None
    try:
        type_lane_text = lane_attributes.find('vehicle').text
        type_lane = 'vehicle'
    except:
        try:
            type_lane_text = lane_attributes.find('bikeLane').text
            type_lane = 'bikeLane'
        except:
            try:
                type_lane_text = lane_attributes.find('crosswalk').text
                type_lane = 'crosswalk'
            except:
                type_lane = None
    return type_lane


def func_connects_to(connects_to, signal_dict):
    """
    This function retrieves and adds the connection_id to the dict.
    :param connects_to: string
    :param signal_dict: dictionary
    :return: connects_to_dict: dictionary
    """
    connection = connects_to.find('connection')
    connecting_lane = connection.find('connectingLane')
    lane = connecting_lane.find('lane').text
    maneuver = connecting_lane.find('maneuver').text
    signal_group = signal_dict[connection.find('signalGroup').text]
    connection_id = connection.find('connectionID').text

    connects_to_dict = {'lane': lane,
                        'maneuver': maneuver,
                        'signalGroup': signal_group,
                        'connectionID': connection_id}

    return connects_to_dict


def func_regional(regional):
    """
    This function retrieves the latitude and longitude in regional.
    :param regional: string
    :return: nodes_regional_list: list
    """
    add_grp_c = regional.find('addGrpC')
    nodes = add_grp_c.find('nodes')
    nodes_regional_list = []

    for s in nodes.findall('nodeXY'):
        for t in s.findall('.//node-LatLon'):
            lat = t.find('lat').text
            lon = t.find('lon').text
            pos = (format_lat_lon(lat, lon))

        regional_dict = {'pos': pos}
        nodes_regional_list.append(regional_dict)
    return nodes_regional_list


def func_sensor_position(sensor_position):
    """
    This function retrieves the starting and ending position of a specific sensor and formats it.
    :param sensor_position: string
    :return: sensor_position: (string, string)
    """
    lat, long = sensor_position.find('lat').text, sensor_position.find('long').text
    lat, long = format_lat_lon(lat, long)
    sensor_position = (lat, long)
    return sensor_position

def func_real_sensor_position(geo_shape):
    """
    This function retrieves the sensor position using the geoshape, (extra precise)
    :param geo_shape: string
    :return: real_sensor_position: (('string', 'string'), ('string', 'string'))
    """
    start_sensor = (format_lat_lon(geo_shape[1].find('lat').text, geo_shape[1].find('long').text))
    end_sensor = (format_lat_lon(geo_shape[2].find('lat').text, geo_shape[2].find('long').text))
    real_sensor_position = start_sensor, end_sensor

    return real_sensor_position
