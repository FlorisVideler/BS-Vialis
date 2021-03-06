import pandas as pd
import json
import os

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import ContinuousSpace
from mesa.time import SimultaneousActivation
from .agents import *

dir_path = os.path.dirname(os.path.realpath(__file__))

# Loads all the information about the lanes.
with open(dir_path + r'\data\lane_done_BOS210.json') as json_file:
    data = json.load(json_file)

# Loads all the information about the sensors.
with open(dir_path + r'\data\sensors_done_BOS210.json') as json_file:
    sensor_data = json.load(json_file)

# Loads all the information about the signalgroups.
with open(dir_path + r'\data\signalgroup_BOS210.json') as json_file:
    sgr_data = json.load(json_file)

# Load the actication data (sensors and traffic light.
activation_data = pd.read_csv(dir_path + r'\data\BOS210.csv', sep=';')


class Traffic(Model):
    """
    A class used to represent a Traffic model.
    Attributes:
        placed_agent_count: The amount of agents placed in simulation.
        sgr_data: The signal group relations data.
        light_dict: The light witht the lane as value.
        data: The sensor and traffic light data.
        finished_car_steps: A list with all the finished cars step amounts.
        finished_car_wait:A list with all the finished cars wait step amounts.
        finished_car_steps_int: The average steps it takes a car to get to it's end point.
        finished_car_wait_int: The average steps a car waits at a red light..
        max_steps: The max amount of steps the simulation will run.
        step_count: The amount of steps the simulation is running for.
    """
    placed_agent_count = 0
    sgr_data = sgr_data
    light_dict = {}

    def __init__(
            self,
            light_11: int = 0,
            light_12: int = 0,
            light_01: int = 0,
            light_03: int = 0,
            light_41: int = 0,
            light_04: int = 0,
            light_05: int = 0,
            width: int = 100,
            height: int = 100,
            max_steps: int = 72000,
            start: int = 252500
    ):
        """
        Constructor for the Traffic class.
        :param light_11: The percentage this light's green time is increased.
        :param light_12: The percentage this light's green time is increased.
        :param light_01: The percentage this light's green time is increased.
        :param light_03: The percentage this light's green time is increased.
        :param light_41: The percentage this light's green time is increased.
        :param light_04: The percentage this light's green time is increased.
        :param light_05: The percentage this light's green time is increased.
        :param width: The width of the model.
        :param height: The height of the model.
        :param max_steps: The max amount of steps the simulation will run.
        :param start: The time the simulation starts at, in steps.
        """
        self.data = activation_data.copy()
        self.finished_car_steps = []
        self.finished_car_wait = []
        self.finished_car_steps_int = 0
        self.finished_car_wait_int = 0
        self.max_steps = max_steps
        self.step_count = start
        self.data_time = self.read_row_col('time')
        self.schedule = SimultaneousActivation(self)
        self.space = ContinuousSpace(width, height, True)
        self.lanes = self.make_intersection()
        self.make_sensors()

        # Traffic light setting
        light_setting = {
            '11': light_11,
            '12': light_12,
            '01': light_01,
            '03': light_03,
            '41': light_41,
            '04': light_04,
            '05': light_05
        }
        self.manipulate_traffic_light_data(light_setting)

        # Sensor accuracy tracker
        self.sensor_on_no_car = 0
        self.sensor_on_car_found = 0

        self.active_loops = {
            '044': 0,
            '054': 0,
            '114': 0,
            '124': 0,
            '014': 0,
            '034': 0
        }

        # Data collector
        self.datacollector = DataCollector(
            model_reporters={'avg_car_steps': 'finished_car_steps_int', 'avg_car_wait': 'finished_car_wait_int'})

        self.running = True

    def calc_finished_car_steps(self) -> int:
        """
        Calculates the average amount of steps that a car needed to take to get to the end.
        :return: The average amount of steps a car takes.
        """
        # Checks if cars are not moving
        if len(self.finished_car_steps) > 0:
            return sum(self.finished_car_steps) / len(self.finished_car_steps)
        else:
            return 0

    def calc_finished_car_wait(self) -> int:
        """
        Calculates the average amount of steps a car is waiting for a red light.
        :return: The average amount a car waits.
        """
        # Checks if cars are waiting
        if len(self.finished_car_wait) > 0:
            return sum(self.finished_car_wait) / len(self.finished_car_wait)
        else:
            return 0

    def read_row_col(self, col: str) -> str:
        """
        Reads the data of a specific column.
        :param col: The column to read.
        :return: The value of the column on the given step.
        """
        return self.data[col][self.step_count]

    def increase_by(self, value_to_increase: int, percent: int) -> float:
        """
        Calculate how many steps the traffic light need to be extra on green.
        :param value_to_increase: Base value.
        :param percent: How much percent longer does the light need to be green.
        :return: The amount of steps needed to reach the increase.
        """
        return value_to_increase / 100 * percent

    def manipulate_traffic_light_data(self, lights: dict) -> None:
        """
        Calculates how many steps the traffic light need to be on for.
        :param lights: A dictionary with the setting of the traffic light.
        :return: None
        """
        for light in lights.keys():
            if lights[light] > 0:
                streak = 0
                to_replace = []
                for index, value in enumerate(self.data[light][self.step_count:self.step_count + self.max_steps]):
                    if value == "#":
                        streak += 1
                    else:
                        if streak > 0:
                            increase_info = self.increase_by(streak, lights[light])
                            orange_index = index + self.step_count
                            orange_value = value
                            while orange_value == 'Z':
                                orange_index += 1
                                try:
                                    orange_value = self.data[light][orange_index]
                                except:
                                    break
                            to_replace.append([index + self.step_count, int(np.round(increase_info)),
                                               orange_index + np.round(increase_info)])
                        streak = 0
                if len(to_replace) > 1:
                    to_replace.pop()
                for i in to_replace:
                    self.check_and_replace_timings(i[0], i[1], i[2], light)

    def check_and_replace_timings(self, replace_index: int, increase: int, orange: int, light: str) -> None:
        """
        Exutaly replaces the timings of the traffic lights. Also makes sure the other lights still work fine.
        :param replace_index: At what index does the replace start.
        :param increase: How many steps does the light need to be on extra.
        :param orange: How long was the light orange.
        :param light: The light ID.
        :return: None
        """
        for col in self.data.columns:
            if col in self.sgr_data[light]:
                crosses = []
                for c in range(replace_index, replace_index + increase):
                    if self.data[col][c] == 'Z' or self.data[col][c] == '#':
                        crosses.append(c)
                if len(crosses) > 0:
                    crosses.append(crosses[-1] + int(self.sgr_data[light][col]) * 10)
                    self.data.loc[crosses[0]: crosses[-1], col] = np.nan

        self.data.loc[replace_index:replace_index + increase, light] = '#'
        self.data.loc[replace_index + increase: orange, light] = 'Z'

    def step(self) -> None:
        """
        A function that mesa requires. Just does a step in the simulation.
        :return: None
        """
        self.data_time = self.read_row_col('time')
        self.step_count += 1

        self.spawn_cars()
        self.finished_car_steps_int = self.calc_finished_car_steps()
        self.finished_car_wait_int = self.calc_finished_car_wait()
        self.datacollector.collect(self)
        self.schedule.step()

    def get_done_cars(self) -> None:
        """
        Removes all the cars from simulation that are done.
        :return: None
        """
        for car in self.schedule.agents:
            if car.agent_type == 'car':
                if not car.active:
                    self.space.remove_agent(car)
                    self.schedule.remove(car)

    def spawn_cars(self) -> None:
        """
        Spawns (or generates, depending on what games you play) the cars.
        The cars spawn when a sensor is activated.
        :return: None
        """
        for loop in self.active_loops.keys():
            sensor_info = self.read_row_col(loop)
            if self.active_loops[loop]:
                if sensor_info != '|':
                    self.active_loops[loop] = 0
            else:
                if sensor_info == '|':
                    if self.active_loops[loop] == 0:
                        for sensor in sensor_data:
                            if sensor['name'] == loop:
                                lane = sensor['laneID']
                        ln = []
                        ln_pos = []
                        list_nodes = self.lanes[lane]['in']['nodes'] + self.lanes[lane]['conn']['nodes'] + \
                                     self.lanes[lane]['out']['nodes']
                        for i in self.lanes[lane]['in']['nodes']:
                            ln.append(i)
                            ln_pos.append(i.pos)
                        for i in self.lanes[lane]['conn']['nodes'] + self.lanes[lane]['out']['nodes']:
                            if i.pos not in ln_pos:
                                ln.append(i)
                                ln_pos.append(i.pos)
                        ln.append(list_nodes[len(list_nodes) - 1])
                        car = Car(self.placed_agent_count, self, self.lanes[lane]['in']['nodes'][0].pos, ln, 0,
                                  self.lanes[lane]['in']['nodes'][0],
                                  self.lanes[lane]['in']['nodes'][1], self.lanes[lane]['out']['nodes'][-1])
                        self.place_agent(car, self.lanes[lane]['in']['nodes'][0].pos)
                    self.active_loops[loop] += 1

    def make_intersection(self) -> dict:
        """
        Function that basically makes the whole intersection: the roads, all the nodes and all the traffic lights.
        Needs to happen in one function because the order is important.
        :return: Dictionary with all the lanes and information about them.
        """
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
        return lanes

    def make_sensors(self) -> None:
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
                if 'gen' in sensor:
                    averaged = tuple(np.average(np.array([start_pos, end_pos]), axis=0))
                    sensor_node = Node(self.placed_agent_count, self, averaged, False, False, sensor['laneID'],
                                       self.light_dict[sensor['laneID']])
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
                agent = Sensor(self.placed_agent_count, self, start_pos, start_pos, end_pos, 0, sensor['name'],
                               sensor['laneID'], sensor['distance'])
                self.place_agent(agent, start_pos)

    def place_agent(self, agent: Agent, pos: tuple) -> None:
        """
        Function that places an agent on the space and adds it to the schedule.
        :param agent: The agent to add.
        :param pos: Where to add the agent.
        :return: None
        """
        self.space.place_agent(agent, pos)
        self.schedule.add(agent)
        self.placed_agent_count += 1
