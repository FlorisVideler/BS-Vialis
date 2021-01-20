from mesa import Agent
import math


def get_next_point(curr_point: tuple, target_point: tuple, distance_between_points: float, distance: float) -> tuple:
    """
    Calculates the next point from a current point, based on an end point.
    :param curr_point: current coordinates.
    :param target_point: target coordinates.
    :param distance_between_points: distance between current point and target point.
    :param distance: distance you want to travel.
    :return: the next coordinates, distance between next point en target point.

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
                 pos,
                 geo_data,
                 index: int = 1,
                 active: bool = True,
                 agent_type: str = "car"
                 ):
        super().__init__(unique_id, model)
        self.geo_data = geo_data
        self.active = active
        self.agent_type = agent_type
        self.pos = pos
        self.index = index
        self.next_pos = self.geo_data[self.index][0] * self.model.space.x_max, self.geo_data[self.index][1] * self.model.space.y_max
        self.dist = abs(math.dist(self.pos, self.next_pos))
        self.speed = self.dist / 10
        self.path = []

    def step(self):
        try:
            next_pos, next_distance_to_next_node = get_next_point(self.pos, self.next_pos, self.dist, self.speed)
            if next_distance_to_next_node <= 0:
                print('next node')
                self.index += 1
                self.pos = self.next_pos
                self.next_pos = self.geo_data[self.index][0] * self.model.space.x_max, self.geo_data[self.index][1] * self.model.space.y_max
                self.dist = abs(math.dist(self.pos, self.next_pos))
                self.speed = self.dist / 10
                next_pos, next_distance_to_next_node = get_next_point(self.pos, self.next_pos, self.dist, self.speed)
                self.speed = next_distance_to_next_node / 10
            self.pos = next_pos
            self.dist = next_distance_to_next_node
        except IndexError:
            print('Car is done')



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
            intersection_id: str,
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
        self.intersection_id = intersection_id

    def get_light_from_lane(self):
        if self.lane_id in self.model.lanes:
            return self.model.lanes[self.lane_id]['in']['nodes'][0].light
        return None

    def step(self):
        data_state = self.model.read_row_col(self.intersection_id, self.sensor_id)
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
            intersection_id: str,
            agent_type: str = 'light'
    ):
        super().__init__(unique_id, model)
        self.pos = pos
        self.state = state
        self.agent_type = agent_type
        self.light_id = light_id
        self.intersection_id = intersection_id

    def step(self):
        data_state = self.model.read_row_col(self.intersection_id, self.light_id)
        if data_state == '#':
            self.state = 2
        elif data_state == 'Z':
            self.state = 1
        else:
            self.state = 0
