import json
import pandas as pd
import pandas as pd
from datetime import datetime
from dateutil import tz

df = pd.read_csv(r'car_data/route1.csv')
for route_number in range(1, 11):
    file_name = 'car_data/route' + str(route_number + 1) + '.csv'
    append_df = pd.read_csv(file_name)
    df = df.append(append_df)



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


# def normalize_item(min_value, max_value, x):
#     return (x - min_value) / (max_value - min_value)


with open('laneset_BOS210.json') as json_file:
    data_BOS210 = json.load(json_file)
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

with open('laneset_BOS211.json') as json_file:
    data_BOS211 = json.load(json_file)
    for lane in data_BOS211:
        if lane['laneAttributes']['type_lane'] == 'vehicle':
            for pos in lane['nodes']:
                all_pos_x.append(float(pos['pos'][0]))
                all_pos_y.append(float(pos['pos'][1]))
            for pos in lane['regional']:
                all_pos_x.append(float(pos['pos'][0]))
                all_pos_y.append(float(pos['pos'][1]))

with open('sensors_list_BOS210.json') as json_file:
    sensor_data_BOS210 = json.load(json_file)

    for sensor in sensor_data_BOS210:
        if sensor['sensorDeviceType'] == 'inductionLoop':
            all_pos_x.append(float(sensor['realSensorPosition'][0][0]))
            all_pos_x.append(float(sensor['realSensorPosition'][1][0]))
            all_pos_y.append(float(sensor['realSensorPosition'][0][1]))
            all_pos_y.append(float(sensor['realSensorPosition'][1][1]))

with open('sensors_list_BOS211.json') as json_file:
    sensor_data_BOS211 = json.load(json_file)

    for sensor in sensor_data_BOS211:
        if sensor['sensorDeviceType'] == 'inductionLoop':
            all_pos_x.append(float(sensor['realSensorPosition'][0][0]))
            all_pos_x.append(float(sensor['realSensorPosition'][1][0]))
            all_pos_y.append(float(sensor['realSensorPosition'][0][1]))
            all_pos_y.append(float(sensor['realSensorPosition'][1][1]))

df['time'] = df['time'].apply(cdt)
df_time = list(df['time'])
df_lat = list(df['lat'])
df_lon = list(df['lon'])
all_pos_x += df_lat
all_pos_y += df_lon

norm_x = normalize(all_pos_x)
norm_y = normalize(all_pos_y)
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

# print(data)

with open('laneset_BOS210_done.json', 'w') as fp:
    json.dump(data_BOS210, fp, indent=4)

with open('laneset_BOS211_done.json', 'w') as fp:
    json.dump(data_BOS211, fp, indent=4)

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

json_obj = []

df_lat = norm_x[-len(df_time):]
df_lon = norm_y[-len(df_time):]

for i in range(len(df_time)):
    time_obj = {
        df_time[i]: [df_lat[i], df_lon[i]]
    }
    json_obj.append([df_lat[i], df_lon[i]])

with open('geodata.json', 'w') as fp:
    json.dump(json_obj, fp, indent=4)
