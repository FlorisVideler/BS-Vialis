import json
import pandas as pd
from datetime import datetime
from dateutil import tz

df = pd.read_csv(r'08-Jan-2021-1318.csv')
with open('C:/Users/jaspe/Downloads/Unity/BS-Vialis/tools/laneset_BOS210.json') as json_file:
    data_BOS210 = json.load(json_file)
with open('C:/Users/jaspe/Downloads/Unity/BS-Vialis/tools/laneset_BOS211.json') as json_file:
    data_BOS211 = json.load(json_file)
with open('C:/Users/jaspe/Downloads/Unity/BS-Vialis/tools/sensors_list_BOS210.json') as json_file:
    sensor_data_BOS210 = json.load(json_file)
with open('C:/Users/jaspe/Downloads/Unity/BS-Vialis/tools/sensors_list_BOS211.json') as json_file:
    sensor_data_BOS211 = json.load(json_file)

def cdt(x):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ')

    utc = utc.replace(tzinfo=from_zone)

    central = utc.astimezone(to_zone)
    central = central.strftime('%d-%m-%Y %H:%M:%S.%f')
    return central



def normalize(array):
    min_array = min(array)
    max_array = max(array)
    z = []
    for i in range(len(array)):
        curr_z = (array[i] - min_array) / (max_array - min_array)
        z.append(curr_z)
    return z

def normalize_this():
    all_pos_x, all_pos_y = set_pos()
    all_pos_x += df_lat
    all_pos_y += df_lon
    norm_x = normalize(all_pos_x)
    norm_y = normalize(all_pos_y)
    return norm_x, norm_y

def set_pos():
    all_pos_x = []
    all_pos_y = []
    for lane in data_BOS210:
        if lane['laneAttributes']['type_lane'] == 'vehicle':
            for pos in lane['nodes']:
                all_pos_x.append(float(pos['pos'][0]))
                all_pos_y.append(float(pos['pos'][1]))
            for pos in lane['regional']:
                all_pos_x.append(float(pos['pos'][0]))
                all_pos_y.append(float(pos['pos'][1]))

    for lane in data_BOS211:
        if lane['laneAttributes']['type_lane'] == 'vehicle':
            for pos in lane['nodes']:
                all_pos_x.append(float(pos['pos'][0]))
                all_pos_y.append(float(pos['pos'][1]))
            for pos in lane['regional']:
                all_pos_x.append(float(pos['pos'][0]))
                all_pos_y.append(float(pos['pos'][1]))

    for sensor in sensor_data_BOS210:
        if sensor['sensorDeviceType'] == 'inductionLoop':
            all_pos_x.append(float(sensor['realSensorPosition'][0][0]))
            all_pos_x.append(float(sensor['realSensorPosition'][1][0]))
            all_pos_y.append(float(sensor['realSensorPosition'][0][1]))
            all_pos_y.append(float(sensor['realSensorPosition'][1][1]))

    for sensor in sensor_data_BOS211:
        if sensor['sensorDeviceType'] == 'inductionLoop':
            all_pos_x.append(float(sensor['realSensorPosition'][0][0]))
            all_pos_x.append(float(sensor['realSensorPosition'][1][0]))
            all_pos_y.append(float(sensor['realSensorPosition'][0][1]))
            all_pos_y.append(float(sensor['realSensorPosition'][1][1]))

    return all_pos_x, all_pos_y


df['time'] = df['time'].apply(cdt)
df_time = list(df['time'])
df_lat = list(df['lat'])
df_lon = list(df['lon'])
norm_x, norm_y = normalize_this()
def dumplaneset():
    i = 0
    for lane in data_BOS210:
        if lane['laneAttributes']['type_lane'] == 'vehicle':
            for pos in lane['nodes']:
                pos['ref_pos'] = [norm_x[i], norm_y[i]]
                i += 1
            for pos in lane['regional']:
                pos['ref_pos'] = [norm_x[i], norm_y[i]]
                i += 1

    for lane in data_BOS211:
        if lane['laneAttributes']['type_lane'] == 'vehicle':
            for pos in lane['nodes']:
                pos['ref_pos'] = [norm_x[i], norm_y[i]]
                i += 1
            for pos in lane['regional']:
                pos['ref_pos'] = [norm_x[i], norm_y[i]]
                i += 1

    with open('laneset_BOS210_done.json', 'w') as fp:
        json.dump(data_BOS210, fp, indent=4)

    with open('laneset_BOS211_done.json', 'w') as fr:
        json.dump(data_BOS211, fr, indent=4)


def dumpsensorset():
    i = 0
    for sensor in sensor_data_BOS210:
        if sensor['sensorDeviceType'] == 'inductionLoop':
            sensor['sensorRefPos'] = [[norm_x[i], norm_y[i]], [norm_x[i + 1], norm_y[i + 1]]]
            i += 2

    for sensor in sensor_data_BOS211:
        if sensor['sensorDeviceType'] == 'inductionLoop':
            sensor['sensorRefPos'] = [[norm_x[i], norm_y[i]], [norm_x[i + 1], norm_y[i + 1]]]
            i += 2

    with open('sensors_list_BOS210_done.json', 'w') as fp:
        json.dump(sensor_data_BOS210, fp, indent=4)

    with open('sensors_list_BOS211_done.json', 'w') as fp:
        json.dump(sensor_data_BOS211, fp, indent=4)

def dump_geo():
    json_obj = []

    df_lat = norm_x[-len(df_time):]
    df_lon = norm_y[-len(df_time):]


    for i in range(len(df_time)):
        time_obj = {df_time[i]: [df_lat[i], df_lon[i]]}
        json_obj.append([df_lat[i], df_lon[i]])


    with open('geodata.json', 'w') as fp:
        json.dump(json_obj, fp, indent=4)
