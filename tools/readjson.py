import json, os
import pandas as pd
from datetime import datetime
from dateutil import tz

main_path = os.path.dirname(os.path.realpath(__file__))
main_path = (os.path.normpath(main_path + os.sep + os.pardir))
print(main_path)

dir_path = os.path.dirname(os.path.realpath(__file__))

def normalize(array):
    # Normalises an array so it fits between 0 and 1.
    min_array = min(array)
    max_array = max(array)
    z = []
    for i in range(len(array)):
        curr_z = (array[i] - min_array) / (max_array - min_array)
        z.append(curr_z)
    return z


def convert_time(x):
    # Converts the time so it uses UTC and fits with current timezone.
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ')

    utc = utc.replace(tzinfo=from_zone)

    central = utc.astimezone(to_zone)
    central = central.strftime('%d-%m-%Y %H:%M:%S.%f')
    return central


def load_data(path):
    # Loads the json file of that path.
    with open(dir_path + '/output/' + path) as json_file:
        return json.load(json_file)


def write_data(path, data, sim):
    if sim:
        with open(main_path + "/traffic_model/simulation/data/" + path, 'w') as fp:
            json.dump(data, fp, indent=4)
    if sim == False:
        with open(main_path + "/traffic_model/visualization/data/" + path, 'w') as fp:
            json.dump(data, fp, indent=4)


def process_lanes_and_sensors(lanes_to_process, sensors_to_process, niels=None, sim=False):
    all_x = []
    all_y = []
    all_lanes = []
    all_sensors = []
    all_routes = []
    total_df_len = 0
    index = 0
    if sim:
        lanes_to_process = ['laneset_BOS210.json']
        sensors_to_process = ['sensors_list_BOS210.json']
        niels = []
    # Add the lane positions to the global list to normalize
    for lanes_file in lanes_to_process:
        lanes_data = load_data(lanes_file)
        all_lanes.append(lanes_data)
        for lane in lanes_data:
            if lane['laneAttributes']['type_lane'] == 'vehicle':
                for pos in lane['nodes']:
                    all_x.append(float(pos['pos'][0]))
                    all_y.append(float(pos['pos'][1]))
                for pos in lane['regional']:
                    all_x.append(float(pos['pos'][0]))
                    all_y.append(float(pos['pos'][1]))
    # Add the sensor positions to the global list to normalize
    for sensors_file in sensors_to_process:
        sensors_data = load_data(sensors_file)
        all_sensors.append(sensors_data)
        for sensor in sensors_data:
            if sensor['sensorDeviceType'] == 'inductionLoop':
                all_x.append(float(sensor['realSensorPosition'][0][0]))
                all_x.append(float(sensor['realSensorPosition'][1][0]))
                all_y.append(float(sensor['realSensorPosition'][0][1]))
                all_y.append(float(sensor['realSensorPosition'][1][1]))

    # Add the positions of Niels's car if needed
    if niels:
        for route_number in niels:
            df_route = pd.read_csv(f'{main_path}/tools/car_data/route{route_number}.csv')
            df_route['time'] = df_route['time'].apply(convert_time)
            total_df_len += len(df_route['time'])
            all_routes.append(df_route)
            all_x += list(df_route['lat'])
            all_y += list(df_route['lon'])

    # Normalize all the positions
    norm_x = normalize(all_x)
    norm_y = normalize(all_y)

    # Now put the data back in place
    # Get the lane positions
    for lanes_data in all_lanes:
        for lane in lanes_data:
            if lane['laneAttributes']['type_lane'] == 'vehicle':
                for pos in lane['nodes']:
                    pos['ref_pos'] = [norm_x[index], norm_y[index]]
                    index += 1
                for pos in lane['regional']:
                    pos['ref_pos'] = [norm_x[index], norm_y[index]]
                    index += 1
        write_data(f'lane_done_{lanes_data[0]["intersectionName"]}.json', lanes_data, sim)

    # Same for the sensors
    for sensors_data in all_sensors:
        for sensor in sensors_data:
            if sensor['sensorDeviceType'] == 'inductionLoop':
                sensor['sensorRefPos'] = [[norm_x[index], norm_y[index]], [norm_x[index + 1], norm_y[index + 1]]]
                index += 2
        write_data(f'sensors_done_{sensors_data[0]["intersectionName"]}.json', sensors_data, sim)

    df_lat = norm_x[-total_df_len:]
    df_lon = norm_y[-total_df_len:]
    index = 0
    for route_index in range(len(all_routes)):
        json_obj = []
        for i in range(len(all_routes[route_index]['time'])):
            json_obj.append([df_lat[index], df_lon[index]])
            index += 1
        write_data(f'route{route_index}.json', json_obj, sim=False)


lanes = ['laneset_BOS210.json', 'laneset_BOS211.json']
sensors = ['sensors_list_BOS210.json', 'sensors_list_BOS211.json']
geo_routes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

if __name__ == '__main__':
    process_lanes_and_sensors(lanes, sensors, geo_routes)
