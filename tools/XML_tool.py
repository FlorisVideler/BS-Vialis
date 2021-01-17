from xml.etree import ElementTree as ET

def load_data(path):
    tree = ET.parse(path)
    root = tree.getroot()
    return root

# deze functie zet de latitude en longitude om naar comma getallen
def format_lan_lon(la, lo):
    la = la[:2] + '.' + la[2:]
    lo = lo[:1] + '.' + lo[1:]
    return la, lo


# deze functie probeert verschillende lanetypes, als de lanetype matcht assignt hij die.
def lane_type(q):
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
    return type_lane


# deze functie haalt verschillende data op uit de XML file en zet die in een dict
def func_connects_to(connects_to, signal_dict):
    connection = connects_to.find('connection')
    connecting_lane = connection.find('connectingLane')
    lane = connecting_lane.find('lane').text
    maneuver = connecting_lane.find('maneuver').text
    signal_group = signal_dict[connection.find('signalGroup').text]
    connection_id = connection.find('connectionID').text
    connects_to_dict = {'lane': lane, 'maneuver': maneuver, 'signalGroup': signal_group,
                        'connectionID': connection_id}

    return connects_to_dict


# deze functie haalt de latitude en longitude op.
def func_regional(regional):
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
    return nodes_regional_list

# deze functie haalt het beginpunt van de sensor op en het eindpunt.
def func_sensor_position(sensor_position):

    lat, long = sensor_position.find('lat').text, sensor_position.find('long').text
    lat, long = lat[:2] + '.' + lat[2:], long[:1] + '.' + long[1:]
    sensor_position = (lat, long)
    return sensor_position

def func_real_sensor_position(geo_shape):
    start_sensor = (format_lan_lon(geo_shape[1].find('lat').text, geo_shape[1].find('long').text))
    end_sensor = (format_lan_lon(geo_shape[2].find('lat').text, geo_shape[2].find('long').text))
    real_sensor_position = start_sensor, end_sensor

    return real_sensor_position