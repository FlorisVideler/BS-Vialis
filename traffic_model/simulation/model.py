import pandas as pd
import json
import random
import os

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import ContinuousSpace
from mesa.time import SimultaneousActivation
from .agents import *

dir_path = os.path.dirname(os.path.realpath(__file__))
print('dp', dir_path)

with open(dir_path + r'\data\lanesetporc.json') as json_file:
    data = json.load(json_file)

with open(dir_path + r'\data\sensorproc.json') as json_file:
    sensor_data = json.load(json_file)


class Traffic(Model):
    def __init__(
            self,
            population=100,
            width=100,
            height=100,
    ):
        self.data = self.load_data(dir_path + r'\data\BOS210.csv')
        self.step_count = 288000
        self.data_time = self.read_row_col('time')
        self.population = population
        self.schedule = SimultaneousActivation(self)
        self.space = ContinuousSpace(width, height, True)
        self.placed_agent_count = 0
        self.light_dict = {}
        self.lanes = self.make_intersection()
        self.make_sensors()
        self.running = True

        # Car stats tracker
        self.finished_car_steps = []
        self.avg_car_steps = 0

        self.finished_car_wait = []
        self.avg_car_wait = 0


        # Sensor accuracy tracker
        self.sensor_on_no_car = 0
        self.sensor_on_car_found = 0

        # Data collector
        self.datacollector = DataCollector(
            model_reporters={'avg_car_steps': 'avg_car_steps', 'avg_car_wait': 'avg_car_wait'})

        self.active_loops = {
            '044': 0,
            '054': 0,
            '114': 0,
            '124': 0,
            '014': 0,
            '034': 0
        }

    def calculate_avg_car_stats(self):
        if len(self.finished_car_steps) > 0:
            self.avg_car_steps = sum(self.finished_car_steps) / len(self.finished_car_steps)
        if len(self.finished_car_wait) > 0:
            self.avg_car_wait = sum(self.finished_car_wait) / len(self.finished_car_wait)

    def load_data(self, path):
        df = pd.read_csv(path, sep=';')
        return df

    def read_row_col(self, col):
        return self.data[col][self.step_count]

    def step(self):
        self.schedule.step()
        self.data_time = self.read_row_col('time')
        self.step_count += 1

        if self.step_count % 100 == 0 :
            print(self.sensor_on_no_car + self.sensor_on_car_found, self.sensor_on_no_car, self.sensor_on_car_found)

        self.spawn_cars()
        self.calculate_avg_car_stats()
        self.datacollector.collect(self)

    def spawn_cars(self):
        for loop in self.active_loops.keys():
            data = self.read_row_col(loop)
            if self.active_loops[loop]:
                if data != '|':
                    self.active_loops[loop] = 0
            else:
                if data == '|':
                    if self.active_loops[loop] == 0:
                        for sensor in sensor_data:
                            if sensor['name'] == loop:
                                lane = sensor['laneID']
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
                        car = Car(self.placed_agent_count, self, self.lanes[lane]['in']['nodes'][0].pos, ln, 0, self.lanes[lane]['in']['nodes'][0],
                                  self.lanes[lane]['in']['nodes'][1], self.lanes[lane]['out']['nodes'][-1])
                        self.place_agent(car, self.lanes[lane]['in']['nodes'][0].pos)
                    self.active_loops[loop] += 1

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
                            traffic_light = Light(self.placed_agent_count, self, posxy, 0,
                                                 lane['connectsTo']['signalGroup'])
                            self.place_agent(traffic_light, posxy)
                            self.light_dict[lane_id] = traffic_light
                    agent = Node(self.placed_agent_count, self, posxy, stop_line, False, lane_id, traffic_light,
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
                                              self.light_dict[lane_id])
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
                        agent = Node(self.placed_agent_count, self, pos, False, True, lane_id, self.light_dict[lane_id])
                        lane_info['conn']['nodes'].append(agent)
                        self.place_agent(agent, pos)
                        if reg_start_node is not None and reg_end_node is None:
                            reg_end_node = agent

                        if reg_start_node is None:
                            reg_start_node = agent

                        if reg_start_node and reg_end_node:
                            road_agent = Road(self.placed_agent_count, self, reg_start_node, reg_end_node,
                                              f'reg_{lane_id}', self.light_dict[lane_id])
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
        for sensor in sensor_data:
            if sensor['sensorDeviceType'] == 'inductionLoop':
                start_pos = sensor['sensorRefPos'][0][0] * self.space.x_max, sensor['sensorRefPos'][0][
                    1] * self.space.y_max
                end_pos = sensor['sensorRefPos'][1][0] * self.space.x_max, sensor['sensorRefPos'][1][
                    1] * self.space.y_max
                if 'gen' in sensor:
                    averaged = tuple(np.average(np.array([start_pos, end_pos]), axis=0))
                    sensor_node = Node(self.placed_agent_count, self, averaged, False, False, sensor['laneID'], self.light_dict[sensor['laneID']])
                    self.place_agent(sensor_node, averaged)
                    last = 999
                    nodes_to_remove = []
                    for i in self.lanes[sensor['laneID']]['in']['nodes']:
                        if math.dist(averaged, i.pos) < last:
                            nodes_to_remove.append(i)
                            last = math.dist(averaged, i.pos)

                    for on in nodes_to_remove:
                        self.lanes[sensor['laneID']]['in']['nodes'].remove(on)
                    self.lanes[sensor['laneID']]['in']['nodes'].insert(0, sensor_node)
                agent = Sensor(self.placed_agent_count, self, start_pos, start_pos, end_pos, 0, sensor['name'], sensor['laneID'], sensor['distance'])
                self.place_agent(agent, start_pos)

    def place_agent(self, agent, pos):
        self.space.place_agent(agent, pos)
        self.schedule.add(agent)
        self.placed_agent_count += 1
