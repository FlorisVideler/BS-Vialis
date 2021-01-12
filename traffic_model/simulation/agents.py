from mesa import Agent
import math


def get_next_point(curr_point: tuple, target_point: tuple, distance_between_points: float, distance: float):
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


class Node(Agent):
    def __init__(
            self,
            unique_id: int,
            model,
            pos: tuple,
            stop_line: bool,
            reg: bool,
            lane_id: int,
            light,
            connecting_lane=None,
            active: bool = True,
            agent_type: str = "node",
    ):
        super().__init__(unique_id, model)
        self.pos = pos
        self.stop_line = stop_line
        self.agent_type = agent_type
        self.reg = reg
        self.active = active
        self.lane_id = lane_id
        self.light = light
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
        self.active = True

    def move_agent(self, new_pos):
        self.pos = new_pos
        self.model.space.move_agent(self, new_pos)

    def get_next_node(self):
        self.current_node = self.next_node
        if self.current_node == self.end_node:
            return False
        self.next_node = self.lane[self.node_index + 2]
        return True

    def stop_car(self):
        self.active = False

    def red_light(self):
        if self.current_node.stop_line and self.current_node.light.state == 0:
            return True
        else:
            return False

    def step(self):
        if not self.red_light():
            next_pos, next_distance_to_next_node = get_next_point(self.pos, self.next_node.pos,
                                                                  self.distance_to_next_node, self.current_speed)
            if next_distance_to_next_node < 0:
                if not self.get_next_node():
                    self.stop_car()
                    return
                self.node_index += 1
                self.move_agent(self.current_node.pos)
                self.distance_to_next_node = math.dist(self.pos, self.next_node.pos)
                next_pos, next_distance_to_next_node = get_next_point(self.pos, self.next_node.pos,
                                                                      self.distance_to_next_node,
                                                                      abs(next_distance_to_next_node))
            self.move_agent(next_pos)
            self.distance_to_next_node = next_distance_to_next_node


class Road(Agent):
    def __init__(
            self,
            unique_id: int,
            model,
            start_node: Node,
            end_node: Node,
            lane_id: str,
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
            lane_id: str,
            distance_from_light: int,
            agent_type: str = "sensor"
    ):
        super().__init__(unique_id, model)
        self.pos = pos
        self.state = state
        self.agent_type = agent_type
        self.sensor_id = sensor_id
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.lane_id = lane_id
        self.distance_from_light = distance_from_light
        self.light = self.get_light_from_lane()

    def get_light_from_lane(self):
        if self.lane_id in self.model.lanes:
            return self.model.lanes[self.lane_id]['in']['nodes'][0].light
        return None

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
