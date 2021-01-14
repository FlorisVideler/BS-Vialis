from xml.etree import ElementTree as ET
import json


files = ['79190154_BOS210_ITF_COMPLETE.xml', '7919015E_BOS211_ITF_COMPLETE.xml']

for file in files:
    tree = ET.parse(file)
    root = tree.getroot()

    lane_set = []

    signal_dict = {}

    for sg in root.findall('.//sg'):
        signal_dict[sg.find('signalGroup').text] = sg.find('name').text

    print(signal_dict)

    def format_lan_lon(la, lo):
        la = la[:2] + '.' + la[2:]
        lo = lo[:1] + '.' + lo[1:]
        return la, lo

    intersection_geometry = root.find('.//intersectionGeometry')
    intersection_name = intersection_geometry.find('name').text
    print(intersection_name)

    for p in root.findall('.//genericLane'):
        lane_id = p.find('laneID').text  # key van dict
        name = p.find('name').text  #
        for q in p.findall('.//laneAttributes'):
            directional_use = q.find('directionalUse').text
            shared_with = q.find('sharedWith').text  # sharded with moet er in
            # Weg soort
            type_lane = None
            try:
                type_lane_text = q.find('vehicle').text
                type_lane = 'vehicle'
            except:
                try:
                    type_lane_text = q.find('bikeLane').text
                    type_lane = 'bikeLane'
                except:
                    try:
                        type_lane_text = q.find('crosswalk').text
                        type_lane = 'crosswalk'
                    except:
                        type_lane = None
            laneattributes_dict = {'directionalUse': directional_use, 'sharedWith': shared_with, 'type_lane': type_lane}
        r = p.find('nodes')
        nodexy_list = []
        all_s = r.findall('nodeXY')

        for s in range(len(all_s)):
            for t in all_s[s].findall('.//node-LatLon'):
                lat = t.find('lat').text
                lon = t.find('lon').text
                pos = (format_lan_lon(lat, lon))
            try:
                u = all_s[s].find('.//attributes')
            except:
                u = None
            if u:  # Als het een attribute heeft gaan we er in zoeken
                local_node = u.find('localNode')
                if not local_node:
                    local_node = u.find('enabled')
                if not local_node:
                    local_node = u.find('disabled')
                try:
                    attribute_text = local_node.find('nodeAttributeXY').text
                except:
                    attribute_text = local_node.find('segmentAttributeXY').text
            else:
                attribute_text = None
            nodes_dict = {'pos': pos, 'attribute': attribute_text}
            nodexy_list.append(nodes_dict)


        connects_to = p.find('connectsTo')
        if connects_to:
            connection = connects_to.find('connection')
            connecting_lane = connection.find('connectingLane')
            lane = connecting_lane.find('lane').text
            maneuver = connecting_lane.find('maneuver').text
            signal_group = signal_dict[connection.find('signalGroup').text]
            connection_id = connection.find('connectionID').text
            connects_to_dict = {'lane': lane, 'maneuver': maneuver, 'signalGroup': signal_group, 'connectionID': connection_id}
            # print(connectsTo_dict) CONNECTTO_DICT IS ALLE CONNECTSTO INFO DIT MOET AAN DE UITEINDELIJKE DICT WORDEN GE-ADD
        regional = p.find('regional')
        if regional:
            add_grp_c = regional.find('addGrpC')
            nodes = add_grp_c.find('nodes')
            nodes_regional_list = []
            for s in nodes.findall('nodeXY'):
                for t in s.findall('.//node-LatLon'):
                    lat = t.find('lat').text
                    lon = t.find('lon').text
                    pos = (format_lan_lon(lat, lon))
                try:
                    u = s.find('.//attributes')
                except:
                    u = None
                if u:  # Als het een attribute heeft gaan we er in zoeken
                    local_node = u.find('localNode')
                    if not local_node:
                        local_node = u.find('enabled')
                    if not local_node:
                        local_node = u.find('disabled')
                    try:
                        attribute_text = local_node.find('nodeAttributeXY').text
                    except:
                        attribute_text = local_node.find('segmentAttributeXY').text
                else:
                    attribute_text = None
                regional_dict = {'pos': pos, 'attribute': attribute_text}
                nodes_regional_list.append(regional_dict)


        generic_lane_dict = {
            'laneID': lane_id,
            'intersectionName': intersection_name,
            'name': name,
            'laneAttributes': laneattributes_dict,
            'nodes': nodexy_list,
            'connectsTo': connects_to_dict,
            'regional': nodes_regional_list
        }
        lane_set.append(generic_lane_dict)

    sensors_list = []

    for sensors in root.findall('.//controlledIntersection'):
        for sensor in sensors.find('sensors'):
            sensor_id = sensor.find('sensorID').text
            name = sensor.find('name').text
            sensor_device_type = sensor.find('sensorDeviceType').text
            sensor_position = None
            real_sensor_position = None
            if sensor_device_type == 'inductionLoop':
                sensor_position = sensor.find('sensorPosition')
                geo_shape = sensor.find('geoShape')
                start_sensor = (format_lan_lon(geo_shape[1].find('lat').text, geo_shape[1].find('long').text))
                end_sensor = (format_lan_lon(geo_shape[2].find('lat').text, geo_shape[2].find('long').text))
                real_sensor_position = start_sensor, end_sensor
                # for index_point in geo_shape:
                #     print(index_point.find('index').text)
                # print(geo_shape)
                lat, long = sensor_position.find('lat').text, sensor_position.find('long').text
                lat, long = lat[:2] + '.' + lat[2:], long[:1] + '.' + long[1:]
                sensor_position = (lat, long)

                sensor_locs = sensor.find('sensorAllocations')
                sensor_loc = sensor_locs.find('sensorAllocation')
                lane_id = sensor_loc.find('laneID').text
                distance = sensor_loc.find('distance').text

            try:
                length = sensor.find('length').text
            except:
                length = None

            sensor = {'sensorID': sensor_id, 'name': name, 'sensorDeviceType': sensor_device_type, 'realSensorPosition': real_sensor_position, 'sensorPosition': sensor_position, 'length': length, 'laneID': lane_id, 'distance': distance, 'intersectionName': intersection_name}
            sensors_list.append(sensor)

    print(lane_set)
    print("\n")
    print(sensors_list)

    with open(f'sensors_list_{intersection_name}.json', 'w') as fp:
        json.dump(sensors_list, fp, indent=4)

    with open(f'laneset_{intersection_name}.json', 'w') as fp:
        json.dump(lane_set, fp, indent=4)
