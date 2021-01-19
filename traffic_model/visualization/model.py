import numpy as np
import pandas as pd
import json
import random

from mesa import Model
from mesa.space import ContinuousSpace
from mesa.time import RandomActivation

from .agents import *

with open('visualization/data/lane_done_BOS210.json') as json_file:
    data_BOS210 = json.load(json_file)

with open('visualization/data/lane_done_BOS211.json') as json_file:
    data_BOS211 = json.load(json_file)

data = data_BOS210 + data_BOS211

with open('visualization/data/sensors_done_BOS210.json') as json_file:
    sensors_list_BOS210 = json.load(json_file)

with open('visualization/data/sensors_done_BOS211.json') as json_file:
    sensors_list_BOS211 = json.load(json_file)

sensor_data = sensors_list_BOS210 + sensors_list_BOS211


class Traffic(Model):
    # TODO: CHECK DEZE TIJDEN?!?!?!?!??!?!?!??!?!?!??!?!
    route_dict = {
            0: 433570,  # 12:02:37.0
            1: 435310,  # 12:05:31.0
            2: 438430,
            3: 440810,
            4: 441910,
            5: 463570,
            6: 464830,
            7: 467240,
            8: 470310,
            9: 472630,
            10: 478650
        }

    def __init__(
            self,
            route=0,
            width=100,
            height=100,
    ):
        self.data = self.load_data({'BOS210': 'visualization/data/BOS210.csv', 'BOS211': 'visualization/data/BOS211.csv'})
        self.geo_data = self.load_geo_data(route)
        self.step_count = self.route_dict[route]
        self.real_step_count = 0
        self.data_time = self.read_row_col('BOS210', 'time')
        self.schedule = RandomActivation(self)
        self.space = ContinuousSpace(width, height, True)
        self.placed_agent_count = 0
        self.lanes = self.make_intersection()
        self.make_sensors()
        self.running = True
        self.niels_car()

    def load_data(self, path, sep=';'):
        data_dict = {}
        for file in path:
            data_dict[file] = pd.read_csv(path[file], sep=sep)
        return data_dict


    def read_row_col(self, intersection, col):
        """
        Reads the data of a specific column.
        :param col: The column to read.
        :return: The value of the column on the given step.
        """
        return self.data[intersection][col][self.step_count]
        # return self.data[col][self.step_count]

    def load_geo_data(self, route):
        with open(f'visualization/data/route{route}.json') as json_file:
            return json.load(json_file)

    def step(self):
        """
        A function that mesa requires. Just does a step in the simulation.
        :return: None
        """
        self.schedule.step()
        self.data_time = self.read_row_col('BOS210', 'time')
        self.step_count += 1
        self.real_step_count += 1

    def niels_car(self):
        print(self.space.x_max, self.space.y_max)
        pos = self.geo_data[0][0] * self.space.x_max, self.geo_data[0][1] * self.space.y_max
        niels = NielsCar(69420, self, pos, self.geo_data)
        self.place_agent(niels, pos)

    def just_test_one_car(self):
        print(list(self.lanes.keys()))
        lane = random.choice(list(self.lanes.keys()))
        print(lane)
        ln = []
        ln_pos = []
        list_nodes = self.lanes[lane]['in']['nodes'] + self.lanes[lane]['conn']['nodes'] + self.lanes[lane]['out']['nodes']
        for i in self.lanes[lane]['in']['nodes']:
            ln.append(i)
            ln_pos.append(i.pos)
        for i in self.lanes[lane]['conn']['nodes'] + self.lanes[lane]['out']['nodes']:
            if i.pos not in ln_pos:
                ln.append(i)
                ln_pos.append(i.pos)

        ln.append(list_nodes[len(list_nodes) - 1])
        car = Car(69420, self, self.lanes[lane]['in']['nodes'][0].pos, ln, 0, self.lanes[lane]['in']['nodes'][0],
                  self.lanes[lane]['in']['nodes'][1], self.lanes[lane]['out']['nodes'][-1])
        self.place_agent(car, self.lanes[lane]['in']['nodes'][0].pos)

    def make_intersection(self):
        """
        Function that basically makes the whole intersection: the roads, all the nodes
        and all the traffic lights.
        Needs to happen in one function because the order is important.
        :return: Dictionary with all the lanes and information about them.
        """
        light_dict = {}
        lanes = {}
        all_lane_nodes = {}
        for lane in data:
            lane_id = lane['laneID']
            if lane['laneAttributes']['type_lane'] == 'vehicle':
                all_lane_nodes[lane_id] = []
                if lane['nodes'][0]['attribute'] == 'stopLine':
                    stop_line_lane = True
                    connecting_lane = lane['connectsTo']['lane']
                    lane_info = {
                        'in': {
                            'nodes': []
                        },
                        'conn': {
                            'nodes': []
                        },
                        'out': {
                            'nodes': []
                        }
                    }
                else:
                    stop_line_lane = False
                    connecting_lane = None

                node_count = 0
                start_node = None
                end_node = None
                reg_start_node = None
                reg_end_node = None
                for pos in range(len(lane['nodes'])):
                    x = lane['nodes'][pos]['ref_pos'][0] * self.space.x_max
                    y = lane['nodes'][pos]['ref_pos'][1] * self.space.y_max

                    attr = lane['nodes'][pos]['attribute']
                    stop_line = False
                    if attr == 'stopLine':
                        stop_line = True

                    posxy = x, y
                    if node_count == 0:
                        node_count += 1
                        if stop_line_lane:
                            taffic_light = Light(self.placed_agent_count, self, posxy, 0,
                                                 lane['connectsTo']['signalGroup'], lane['intersectionName'])
                            self.place_agent(taffic_light, posxy)
                            light_dict[lane_id] = taffic_light
                    agent = Node(self.placed_agent_count, self, posxy, stop_line, False, lane_id, taffic_light,
                                 connecting_lane)
                    self.place_agent(agent, posxy)
                    all_lane_nodes[lane_id].append(agent)
                    if stop_line_lane:
                        lane_info['in']['nodes'].append(agent)

                    if start_node is not None and end_node is None:
                        end_node = agent

                    if start_node is None:
                        start_node = agent

                    if start_node and end_node:
                        if stop_line_lane:
                            road_agent = Road(self.placed_agent_count, self, start_node, end_node, lane_id,
                                              light_dict[lane_id])
                        else:
                            road_agent = Road(self.placed_agent_count, self, start_node, end_node, lane_id)
                        self.place_agent(road_agent, road_agent.start_node.pos)
                        start_node = end_node
                        end_node = None

                if stop_line_lane:
                    lane_info['in']['nodes'].reverse()
                    # Add the nodes on the intersection
                    for pos in lane['regional']:
                        x = pos['ref_pos'][0] * self.space.x_max
                        y = pos['ref_pos'][1] * self.space.y_max
                        pos = x, y
                        agent = Node(self.placed_agent_count, self, pos, False, True, 0, light_dict[lane_id])
                        lane_info['conn']['nodes'].append(agent)
                        self.place_agent(agent, pos)
                        if reg_start_node is not None and reg_end_node is None:
                            reg_end_node = agent

                        if reg_start_node is None:
                            reg_start_node = agent

                        if reg_start_node and reg_end_node:
                            road_agent = Road(self.placed_agent_count, self, reg_start_node, reg_end_node,
                                              f'reg_{lane_id}', light_dict[lane_id])
                            self.place_agent(road_agent, reg_start_node.pos)
                            reg_start_node = reg_end_node
                            reg_end_node = None
                    lanes[lane_id] = lane_info

        for l in all_lane_nodes:
            if all_lane_nodes[l][0].connecting_lane:
                connection = all_lane_nodes[all_lane_nodes[l][0].connecting_lane]
                lanes[l]['out']['nodes'] = connection
                # ADD check voor dubbele cords

        return lanes

    def make_sensors(self):
        """
        Function that places all the sensors.
        :return: None
        """
        for sensor in sensor_data:
            if sensor['sensorDeviceType'] == 'inductionLoop':
                start_pos = sensor['sensorRefPos'][0][0] * self.space.x_max, sensor['sensorRefPos'][0][
                    1] * self.space.y_max
                end_pos = sensor['sensorRefPos'][1][0] * self.space.x_max, sensor['sensorRefPos'][1][
                    1] * self.space.y_max
                agent = Sensor(self.placed_agent_count, self, start_pos, start_pos, end_pos, 0, sensor['name'], sensor['laneID'], sensor['distance'], sensor['intersectionName'])
                self.place_agent(agent, start_pos)

    def place_agent(self, agent, pos):
        """
        Function that places an agent on the space and adds it to the schedule.
        :param agent: The agent to add.
        :param pos: Where to add the agent.
        :return: None
        """
        self.space.place_agent(agent, pos)
        self.schedule.add(agent)
        self.placed_agent_count += 1
