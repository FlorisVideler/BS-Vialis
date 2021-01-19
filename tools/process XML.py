import json
from XML_tool import *

files = ['input/79190154_BOS210_ITF_COMPLETE.xml', 'input/7919015E_BOS211_ITF_COMPLETE.xml']

for file in files:
    tree = ET.parse(file)
    root = tree.getroot()

    lane_set = []

    signal_dict = {}

    for sg in root.findall('.//sg'):
        signal_dict[sg.find('signalGroup').text] = sg.find('name').text

    intersection_geometry = root.find('.//intersectionGeometry')
    intersection_name = intersection_geometry.find('name').text

    # Retrieves laneID and Name
    for generic_Lane in root.findall('.//genericLane'):
        lane_id = generic_Lane.find('laneID').text
        name = generic_Lane.find('name').text

        # Creates a dict with the directionalUse, sharedWith and type_lane.
        for lane_Attributes in generic_Lane.findall('.//laneAttributes'):
            directional_use = lane_Attributes.find('directionalUse').text
            shared_with = lane_Attributes.find('sharedWith').text
            lane_attributes_dict = {'directionalUse': directional_use,
                                    'sharedWith': shared_with,
                                    'type_lane': lane_type(lane_Attributes)}

        nodes = generic_Lane.find('nodes')
        all_s = nodes.findall('nodeXY')
        node_xy_list = []

        # retrieves the latitude and longitudes from the nodes
        for i in range(len(all_s)):
            for node_XY in all_s[i].findall('.//node-LatLon'):
                lat = node_XY.find('lat').text
                lon = node_XY.find('lon').text
                pos = (format_lat_lon(lat, lon))

            u = all_s[i].find('.//attributes')

            # If the attribute exists we find/assign it here.
            attribute_text = None
            if u:
                local_node = u.find('localNode')
                if not local_node:
                    local_node = u.find('enabled')
                if not local_node:
                    local_node = u.find('disabled')
                try:
                    attribute_text = local_node.find('nodeAttributeXY').text
                except:
                    attribute_text = local_node.find('segmentAttributeXY').text

            nodes_dict = {'pos': pos, 'attribute': attribute_text}
            node_xy_list.append(nodes_dict)

        # Creates the connects_to_dict
        connects_to = generic_Lane.find('connectsTo')
        if connects_to:
            connects_to_dict = (func_connects_to(connects_to, signal_dict))

        # Creates a list with all the regional nodes
        regional = generic_Lane.find('regional')
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

    # Retrieves all the sensor characteristics and adds them to a list
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

            sensor = {'sensorID': sensor_id, 'name': name, 'sensorDeviceType': sensor_device_type,
                      'realSensorPosition': real_sensor_position, 'sensorPosition': sensor_position,
                      'length': length, 'laneID': lane_id, 'distance': distance,
                      'intersectionName': intersection_name}

            sensors_list.append(sensor)

    # Writes the retrieved and formatted data to a json file so we it's usable.

    with open(f'output/sensors_list_{intersection_name}.json', 'w') as fp:
        json.dump(sensors_list, fp, indent=4)

    with open(f'output/laneset_{intersection_name}.json', 'w') as fp:
        json.dump(lane_set, fp, indent=4)


