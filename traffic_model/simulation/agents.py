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
        self.next_pos = None
        self.active = True
        self.passed_light = False

        self.acceleration = 0.05722366187130742  # 1.25 km/h
        self.current_speed = 0
        self.max_speed = 2.2889464748522967  # 50km/h

        # 1m = 1.6480414618936536 px
        # 50km/h = 1.3888888888888888 m per step (0.1 s)
        # 50km/h =  2.2889464748522967 px per step

    def get_next_car(self, radius):
        neighbors = self.model.space.get_neighbors(self.pos, radius, False)
        dist_to_end = math.dist(self.pos, self.end_node.pos)
        cars_in_front = {}
        for n in neighbors:
            if n.agent_type == 'car':
                if n.active:
                    if n.next_node.lane_id == self.next_node.lane_id:
                        n_dist_end = math.dist(n.pos, self.end_node.pos)
                        if dist_to_end > n_dist_end:
                            cars_in_front[n_dist_end] = n
        if len(cars_in_front) > 0:
            next_car = cars_in_front[max(list(cars_in_front.keys()))]
            return next_car, math.dist(self.pos, next_car.pos)
        else:
            return None

    def get_distance_to_light(self):
        return math.dist(self.pos, self.lane[0].light.pos), self.lane[0].light.state


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

    def brake(self):
        pass

    def advance(self):
        self.move_agent(self.next_pos)

    def step(self):
        print(self.get_distance_to_light())
        # print(self.unique_id, self.current_node.lane_id, self.next_node.lane_id)
        if not self.red_light():
            dist_to_light = self.get_distance_to_light()
            if dist_to_light[0] <= 50 and dist_to_light[1] == 0:
                self.current_speed -= self.acceleration
            else:
                if self.current_speed < self.max_speed:
                    self.current_speed += self.acceleration

            next_car = self.get_next_car(60)
            if next_car:
                if next_car[1] <= self.current_speed + 15:
                    self.current_speed = next_car[1] - 10  # Hier moet nog een getal vanaf

            print(self.get_distance_to_light())


            if self.current_speed < 0:
                self.current_speed = 0
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
            self.next_pos = next_pos
            self.distance_to_next_node = next_distance_to_next_node
        else:
            self.current_speed = 0
            print("RED LIGHT")
        # print('speed', self.current_speed)


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
