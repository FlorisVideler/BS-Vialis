from xml.etree import ElementTree as ET
import json
from XML_tool import *
files = ['79190154_BOS210_ITF_COMPLETE.xml', '7919015E_BOS211_ITF_COMPLETE.xml']

for file in files:
    root = load_data(f'input/{file}')

    lane_set = []

    signal_dict = {}

    for sg in root.findall('.//sg'):
        signal_dict[sg.find('signalGroup').text] = sg.find('name').text

    intersection_geometry = root.find('.//intersectionGeometry')
    intersection_name = intersection_geometry.find('name').text

    for p in root.findall('.//genericLane'):
        lane_id = p.find('laneID').text
        name = p.find('name').text

        for q in p.findall('.//laneAttributes'):
            directional_use = q.find('directionalUse').text
            shared_with = q.find('sharedWith').text
            lane_attributes_dict = {'directionalUse': directional_use,
                                    'sharedWith': shared_with,
                                    'type_lane': lane_type(q)}

        r = p.find('nodes')
        node_xy_list = []
        all_s = r.findall('nodeXY')

        for s in range(len(all_s)):
            for t in all_s[s].findall('.//node-LatLon'):
                lat = t.find('lat').text
                lon = t.find('lon').text
                pos = (format_lan_lon(lat, lon))
            # Zoekt de atributen
            try:
                u = all_s[s].find('.//attributes')

            # Als er een map tussen zit kijkt hij eerst of het enabled/disabled voordat hij bij de attributen komt.
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
            node_xy_list.append(nodes_dict)

        # maakt de connects_to_dict aan.
        connects_to = p.find('connectsTo')
        if connects_to:
            connects_to_dict = (func_connects_to(connects_to, signal_dict))

        # maakt een lijst aan met regional nodes

        regional = p.find('regional')
        if regional:
            add_grp_c = regional.find('addGrpC')
            nodes = add_grp_c.find('nodes')
            nodes_regional_list = func_regional(regional)

        generic_lane_dict = {
            'laneID': lane_id,
            'name': name,
            'laneAttributes': lane_attributes_dict,
            'nodes': node_xy_list,
            'connectsTo': connects_to_dict,
            'regional': nodes_regional_list,
            'intersectionName': intersection_name
        }
        lane_set.append(generic_lane_dict)

    # haalt eigenschappen van de sensoren op en zet die in een lijst
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

                sensor_position = func_sensor_position(sensor_position)
                real_sensor_position = func_real_sensor_position(geo_shape)
                sensor_locs = sensor.find('sensorAllocations')
                sensor_loc = sensor_locs.find('sensorAllocation')
                lane_id = sensor_loc.find('laneID').text
                distance = sensor_loc.find('distance').text

            try:
                length = sensor.find('length').text
            except:
                length = None

            sensor = {'sensorID': sensor_id, 'name': name,
                    'sensorDeviceType': sensor_device_type,
                    'realSensorPosition': real_sensor_position,
                    'sensorPosition': sensor_position, 'length': length,
                    'laneID': lane_id, 'distance': distance, 'intersectionName': intersection_name}
            sensors_list.append(sensor)




    with open(f'output/sensors_list_{intersection_name}.json', 'w') as fp:
        json.dump(sensors_list, fp, indent=4)

    with open(f'output/laneset_{intersection_name}.json', 'w') as fp:
        json.dump(lane_set, fp, indent=4)

#print(lane_set)


#intersection name bij laneset
#regional nodes