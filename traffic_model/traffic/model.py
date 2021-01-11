"""
Flockers
=============================================================
A Mesa implementation of Craig Reynolds's Boids flocker model.
"""

import numpy as np
import pandas as pd
import json

from mesa import Model
from mesa.space import ContinuousSpace
from mesa.time import RandomActivation

from .agents import *

with open(r'C:\Users\Floris Videler\Desktop\School\BS\simulatie\lanesetporc.json') as json_file:
    data = json.load(json_file)

with open(r'C:\Users\Floris Videler\Desktop\School\BS\simulatie\sensorproc.json') as json_file:
    sensor_data = json.load(json_file)


class BoidFlockers(Model):
    """
    Flocker model class. Handles agent creation and placement
    """

    def __init__(
            self,
            population=100,
            width=100,
            height=100,
    ):
        """
        Create a new Flockers model.

        Args:
            population: Number of Boids
            width, height: Size of the space.
                    keep from any other"""
        self.data = self.load_data(r'C:\Users\Floris Videler\Desktop\School\BS\simulatie\BOS210.csv')
        self.step_count = 288002
        self.data_time = self.read_row_col('time')
        self.population = population
        self.schedule = RandomActivation(self)
        self.space = ContinuousSpace(width, height, True)
        self.make_agents()
        self.running = True

    def load_data(self, path):
        df = pd.read_csv(path, sep=';')
        filter_col = [col for col in df if col.startswith('light_')]
        df[filter_col] = df[filter_col].fillna(0)
        return df

    def read_row_col(self, col):
        return self.data[col][self.step_count]

    def step(self):
        self.schedule.step()
        self.data_time = self.read_row_col('time')
        self.step_count += 1

    def make_agents(self):
        """
        Create self.population agents, with random positions
        """
        c = 0
        roads = []
        lights = []
        light_dict = {}
        stop_line_lane = False
        for lane in data:
            if lane['laneAttributes']['type_lane'] == 'vehicle':
                if lane['nodes'][0]['attribute'] == 'stopLine':
                    stop_line_lane = True
                else:
                    stop_line_lane = False
                lane_id = lane['laneID']
                node_count = 0
                begin_road_node = None
                start_node = None
                end_node = None
                reg_start_node = None
                reg_end_node = None
                for pos in range(len(lane['nodes'])):
                    c += 1
                    x = lane['nodes'][pos]['ref_pos'][0] * self.space.x_max
                    y = lane['nodes'][pos]['ref_pos'][1] * self.space.y_max
                    real_x = lane['nodes'][pos]['pos'][0]
                    real_y = lane['nodes'][pos]['pos'][1]
                    look_up = f'{real_x}, {real_y}'

                    attr = lane['nodes'][pos]['attribute']
                    stop_line = False
                    if attr == 'stopLine':
                        stop_line = True

                    last_node = False
                    if pos + 1 == len(lane['nodes']):
                        last_node = True

                    posxy = x, y
                    if node_count == 0:
                        if stop_line_lane:
                            taffic_light = Light(c + len(lights) + 9999, self, posxy, 0,
                                                 lane['connectsTo']['signalGroup'])
                            self.space.place_agent(taffic_light, posxy)
                            self.schedule.add(taffic_light)
                            light_dict[lane_id] = taffic_light
                    agent = Node(c, self, posxy, stop_line, False, lane_id, look_up, taffic_light, last_node)

                    if start_node is not None and end_node is None:
                        end_node = agent

                    if start_node is None:
                        start_node = agent

                    if start_node and end_node:
                        if start_node.lane_id != end_node.lane_id:
                            print(start_node.lane_id, end_node.lane_id)
                        if stop_line_lane:
                            road_agent = Road(len(roads) + c + 999, self, start_node, end_node, lane_id, last_node,
                                              light_dict[lane_id])
                        else:
                            road_agent = Road(len(roads) + c + 999, self, start_node, end_node, lane_id, last_node)
                        # self.space.place_agent(road_agent, pos)
                        # self.schedule.add(road_agent)
                        roads.append(road_agent)
                        start_node = end_node
                        end_node = None
                    # print(len(roads))

                    self.space.place_agent(agent, posxy)
                    self.schedule.add(agent)
                    node_count += 1
                if stop_line_lane:
                    for pos in lane['regional']:
                        c += 1
                        x = pos['ref_pos'][0] * self.space.x_max
                        y = pos['ref_pos'][1] * self.space.y_max
                        pos = x, y
                        agent = Node(c, self, pos, False, True, 0, look_up, light_dict[lane_id])
                        self.space.place_agent(agent, pos)
                        self.schedule.add(agent)
                        if reg_start_node is not None and reg_end_node is None:
                            reg_end_node = agent

                        if reg_start_node is None:
                            reg_start_node = agent

                        if reg_start_node and reg_end_node:
                            road_agent = Road(len(roads) + c + 999, self, reg_start_node, reg_end_node,
                                              f'reg_{lane_id}', False, light_dict[lane_id])
                            roads.append(road_agent)
                            reg_start_node = reg_end_node
                            reg_end_node = None

        for sensor in sensor_data:
            if sensor['sensorDeviceType'] == 'inductionLoop':
                c += 1
                start_pos = sensor['sensorRefPos'][0][0] * self.space.x_max, sensor['sensorRefPos'][0][
                    1] * self.space.y_max
                end_pos = sensor['sensorRefPos'][1][0] * self.space.x_max, sensor['sensorRefPos'][1][
                    1] * self.space.y_max
                agent = Sensor(c, self, start_pos, start_pos, end_pos, 0, sensor['name'])
                self.space.place_agent(agent, start_pos)
                self.schedule.add(agent)

        l = 0
        for road in roads:
            # if l == 38:
            self.space.place_agent(road, road.start_node.pos)
            self.schedule.add(road)
            hmmm_node = road
            # print('hmm')
            l += 1

        # for i in range(len(roads)):
        #     if i > len(roads)-28:
        #         self.space.place_agent(roads[i], roads[i].start_node.pos)
        #         self.schedule.add(roads[i])

        # for i in range(len(x_node_list)):
        #     x = x_node_list[i] * self.space.x_max
        #     y = y_node_list[i] * self.space.y_max
        #     pos = np.array((x, y))
        #     boid = Boid(
        #         i,
        #         self,
        #         pos,
        #         'node'
        #     )
        #     self.space.place_agent(boid, pos)
        #     self.schedule.add(boid)
        #
        # for i in range(len(x_loop_list)):
        #     x = x_loop_list[i] * self.space.x_max
        #     y = y_loop_list[i] * self.space.y_max
        #     pos = np.array((x, y))
        #     boid = Boid(
        #         i + node_len,
        #         self,
        #         pos,
        #         'loop'
        #     )
        #     self.space.place_agent(boid, pos)
        #     self.schedule.add(boid)

    def step(self):
        self.schedule.step()
        self.data_time = self.read_row_col('time')
        self.step_count += 1
