from mesa import Agent
import math


class Lane:
    def __init__(self, lane_id: str, nodes: list):
        self.lane_id = lane_id
        self.nodes = nodes


class Node(Agent):
    def __init__(
            self,
            unique_id: int,
            model,
            pos: tuple,
            stop_line: bool,
            reg: bool,
            lane_id: int,
            real_pos: str,
            light,
            last_node: bool = False,
            active: bool = True,
            agent_type: str = "node",
            connecting_lane=None
    ):
        super().__init__(unique_id, model)
        self.pos = pos
        self.stop_line = stop_line
        self.agent_type = agent_type
        self.reg = reg
        self.active = active
        self.lane_id = lane_id
        self.real_pos = real_pos
        self.light = light
        self.last_node = last_node
        self.connecting_lane = connecting_lane


class Car(Agent):
    def __init__(self,
                 unique_id: int,
                 model,
                 pos: tuple,
                 lane: list,
                 node_index: int,
                 current_node: Node,
                 next_node: Node,
                 end_node: Node,

                 agent_type: str = "car"
                 ):
        super().__init__(unique_id, model)
        self.pos = pos
        self.current_node = current_node
        self.next_node = next_node
        self.end_node = end_node
        self.agent_type = agent_type
        self.lane = lane
        self.node_index = node_index
        self.distance_to_next_node = math.dist(self.pos, self.next_node.pos)
        self.current_speed = 1

    def get_next_point(self, curr_point, target_point, distance_between_points, distance):
        """
        :param curr_point: current coordinates
        :param target_point: target coordinates
        :param distance_between_points: distance between current point and target point
        :param distance: distance you want to travel
        :return: the next coordinates, distance between next point en target point
        """
        x = target_point[0] - curr_point[0]
        y = target_point[1] - curr_point[1]
        factor = distance / distance_between_points
        next_point = (curr_point[0] + (x * factor), curr_point[1] + (y * factor))
        return next_point, distance_between_points - distance

    def step(self):
        next_pos, next_distance_to_next_node = self.get_next_point(self.pos, self.next_node.pos,
                                                                   self.distance_to_next_node, self.current_speed)
        print(next_distance_to_next_node)
        if next_distance_to_next_node < 0:
            print('MINDER DAN 0')
            self.current_node = self.next_node
            if self.current_node == self.end_node:
                return
            self.next_node = self.lane[self.node_index + 2]
            self.node_index += 1
            print(self.current_node.pos, self.next_node.pos)
            self.pos = self.current_node.pos
            self.distance_to_next_node = math.dist(self.pos, self.next_node.pos)
            print(self.distance_to_next_node)
            next_pos, next_distance_to_next_node = self.get_next_point(self.pos, self.next_node.pos,
                                                                       self.distance_to_next_node, abs(next_distance_to_next_node))
        self.pos = next_pos
        self.distance_to_next_node = next_distance_to_next_node


class Road(Agent):
    def __init__(
            self,
            unique_id: int,
            model,
            start_node: Node,
            end_node: Node,
            lane_id: str,
            start: bool = True,
            light=None,
            active: bool = True,
            agent_type: str = "road"
    ):
        super().__init__(unique_id, model)
        self.start_node = start_node
        self.end_node = end_node
        self.lane_id = lane_id
        self.agent_type = agent_type
        self.active = active
        self.light = light
        self.start = start


class Sensor(Agent):
    def __init__(
            self,
            unique_id: int,
            model,
            pos: tuple,
            start_pos: tuple,
            end_pos: tuple,
            state: int,
            sensor_id: str,
            agent_type: str = "sensor"
    ):
        super().__init__(unique_id, model)
        self.pos = pos
        self.state = state
        self.agent_type = agent_type
        self.sensor_id = sensor_id
        self.start_pos = start_pos
        self.end_pos = end_pos

    def step(self):
        data_state = self.model.read_row_col(self.sensor_id)
        if data_state != "|":
            self.state = 0
        else:
            self.state = 1


class Light(Agent):
    def __init__(
            self,
            unique_id: int,
            model,
            pos: tuple,
            state: int,
            light_id: str,
            agent_type: str = 'light'
    ):
        super().__init__(unique_id, model)
        self.pos = pos
        self.state = state
        self.agent_type = agent_type
        self.light_id = light_id

    def step(self):
        data_state = self.model.read_row_col(self.light_id)
        if data_state == '#':
            self.state = 2
        elif data_state == 'Z':
            self.state = 1
        else:
            self.state = 0
