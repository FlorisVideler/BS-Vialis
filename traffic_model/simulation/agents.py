from mesa import Agent
import math
import numpy as np


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
    """
    A class used to represent a Node used to form a Road.
    Attributes:
        pos: A x, y position tuple.
        stop_line: Whether this node is a stop line or not.
        agent_type: What type of agent this is.
        reg: Whether this node is a regional node or not.
        active:Whether this node is active or not.
        lane_id: The id of the lane this node is a part of.
        light: The light that controls the traffic traveling over this node.
        connecting_lane: The id of the lane this node is connecting to.
    """

    def __init__(
            self,
            unique_id: int,
            model: Model,
            pos: tuple,
            stop_line: bool,
            reg: bool,
            lane_id: int,
            light: Light,
            connecting_lane: str = None,
            active: bool = True,
            agent_type: str = "node",
    ):
        """
        Constructor for the Node class.
        :param unique_id: The unique agent ID.
        :param model: The model where the agent is in.
        :param pos: A x, y position tuple.
        :param stop_line: Whether this node is a stop line or not.
        :param reg: Whether this node is a regional node or not.
        :param lane_id: The id of the lane this node is a part of.
        :param light: The light that controls the traffic traveling over this node.
        :param connecting_lane: The id of the lane this node is connecting to.
        :param active: Whether this node is active or not.
        :param agent_type: What type of agent this is.
        """
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
    """
    A class used to represent a Car, used to drive in the simulation

    1px = 0.6067808505563733m
    1m = 1.6480414618936536 px
    50km/h = 1.3888888888888888 m per step (0.1 s)
    50km/h =  2.2889464748522967 px per step

    Attributes:
        next_pos: The next position the car wants to move to. X, y tuple.
        active: Whether the car is active or not.
        steps_active: How many steps the car has been active.
        wait_at_light: How many steps the car has bee waiting at a red light.
        acceleration: The amount om pixels per step the car wants accelerate at.
        max_speed: The amount of pixels per step the car is allowed to move.
        pos: A x, y position tuple.
        current_node: The current node the car is at.
        next_node: The next node, where the car is moving to.
        end_node: The final node, the car stops at this node.
        agent_type: What type of agent this is.
        lane: The lane which the car is driving on.
        node_index: The current node index the car is at.
        distance_to_next_node: The distance in pixels to the next node.
        current_speed: The current amountof pixels per step the car is moving at.
    """
    next_pos = None
    active = True
    steps_active = 0
    wait_at_light = 0
    acceleration = 0.05722366187130742  # 1.25 km/h
    max_speed = 2.2889464748522967  # 50km/h

    def __init__(self,
                 unique_id: int,
                 model: Model,
                 pos: tuple,
                 lane: list,
                 node_index: int,
                 current_node: Node,
                 next_node: Node,
                 end_node: Node,
                 agent_type: str = "car"
                 ):
        """
        Constructor for the Car class.
        :param unique_id: The unique agent ID.
        :param model: The model where the agent is in.
        :param pos: A x, y position tuple.
        :param lane: The lane which the car is driving on.
        :param node_index: The current node index the car is at.
        :param current_node: The current node the car is at.
        :param next_node: The next node, where the car is moving to.
        :param end_node: The final node, the car stops at this node.
        :param agent_type: What type of agent this is.
        """
        super().__init__(unique_id, model)
        self.pos = pos
        self.current_node = current_node
        self.next_node = next_node
        self.end_node = end_node
        self.agent_type = agent_type
        self.lane = lane
        self.node_index = node_index
        self.distance_to_next_node = math.dist(self.pos, self.next_node.pos)
        self.current_speed = self.max_speed

    def get_next_car(self, radius: int) -> tuple:
        """
        Gets the next car object and the distance to it.
        :param radius: How far do we scan for the next car.
        :return: A tuple with a car object and how far away it is. If there are no cars found, None is returned.
        """
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

    def get_distance_to_light(self) -> tuple:
        """
        Calculates distance from self to traffic light.
        :return: A tuple with the distance to the light and the state of the light.
        """
        return math.dist(self.pos, self.lane[0].light.pos), self.lane[0].light.state

    def move_agent(self, new_pos: tuple) -> None:
        """
        Moves the agent to the new position.
        :param new_pos: a tuple with x, y position.
        :return: None.
        """
        # Moves agent
        self.pos = new_pos
        self.model.space.move_agent(self, new_pos)

    def get_next_node(self) -> bool:
        """
        Checks if there is another node to move to.
        :return: True if a next node is found, False if not.
        """
        # Gets the next node to move to
        self.current_node = self.next_node
        if self.current_node == self.end_node:
            return False
        self.next_node = self.lane[self.node_index + 2]
        return True

    def stop_car(self) -> None:
        """
        Stops the car and submits all the statistics.
        :return: None.
        """
        # Stops car
        self.model.finished_car_steps.append(self.steps_active)
        self.model.finished_car_wait.append(self.wait_at_light)
        self.active = False

    def red_light(self) -> bool:
        """
        Function that checks if the car is in front of a red light and is already at the stop line.
        :return: True if car is standing at a red light, otherwise return False.
        """
        if self.current_node.stop_line and self.current_node.light.state == 0:
            return True
        else:
            return False

    def check_light_distance(self) -> None:
        """
        Checks if the car is approaching a red light, if so brake.
        :return: None
        """
        dist_to_light = self.get_distance_to_light()
        if dist_to_light[0] <= 80 and dist_to_light[1] == 0:  # 80px = 48.54246804450987m
            self.current_speed -= (self.acceleration / 2)
        else:
            if self.current_speed < self.max_speed:
                self.current_speed += self.acceleration

    def check_next_car(self) -> None:
        """
        Checks if there is a car in front of self, if so brake so you don't end up in another cars trunk.
        :return: None.
        """
        next_car = self.get_next_car(60)
        if next_car:
            if next_car[1] <= self.current_speed + 15:  # 15px = 9.1017127583456m
                self.current_speed = next_car[1] - 15  # Hier moet nog een getal vanaf

    def move_to_next_node(self) -> bool:
        """
        Gets the next node for a car to move to, if available.
        :return: If a node is available: True, else False.
        """
        if not self.get_next_node():
            self.stop_car()
            return False
        self.node_index += 1
        self.move_agent(self.current_node.pos)
        self.distance_to_next_node = math.dist(self.pos, self.next_node.pos)
        return True

    def advance(self) -> None:
        """
        A function that Mesa requires to work, moves the agent.
        :return: None.
        """
        self.move_agent(self.next_pos)

    def step(self) -> None:
        """
        A function that Mesa requires, takes care of all the car logic.
        :return: None
        """
        if self.active:
            self.steps_active += 1
            if not self.red_light():
                self.check_light_distance()

                self.check_next_car()

                if self.current_speed < 0:
                    self.current_speed = 0
                next_pos, next_distance_to_next_node = get_next_point(self.pos, self.next_node.pos,
                                                                      self.distance_to_next_node, self.current_speed)
                if next_distance_to_next_node < 0:
                    if self.move_to_next_node():
                        next_pos, next_distance_to_next_node = get_next_point(self.pos, self.next_node.pos,
                                                                              self.distance_to_next_node,
                                                                              abs(next_distance_to_next_node))
                    else:
                        return
                self.next_pos = next_pos
                self.distance_to_next_node = next_distance_to_next_node
            else:
                self.current_speed = 0
                self.wait_at_light += 1


class Road(Agent):
    """
    A class used to represent a Road, used to connect two nodes. Mainly used for visualisation.
    Attributes:
        start_node: The node from where the road starts.
        end_node: The node where the roads ends.
        lane_id: The lane id of the lane this road is forming.
        agent_type: What type of agent this is.
        active: Whether this road is active or not.
        light: The light that controls the lane this road is forming.
    """

    def __init__(
            self,
            unique_id: int,
            model: Model,
            start_node: Node,
            end_node: Node,
            lane_id: str,
            light: Light = None,
            active: bool = True,
            agent_type: str = "road"
    ):
        """
        Constructor for the Road class.
        :param unique_id: The unique agent ID.
        :param model: The model where the agent is in.
        :param start_node: The node from where the road starts.
        :param end_node: The node where the roads ends.
        :param lane_id: The lane id of the lane this road is forming.
        :param light: The light that controls the lane this road is forming.
        :param active: Whether this road is active or not.
        :param agent_type: What type of agent this is.
        """
        super().__init__(unique_id, model)
        self.start_node = start_node
        self.end_node = end_node
        self.lane_id = lane_id
        self.agent_type = agent_type
        self.active = active
        self.light = light


class Sensor(Agent):
    """
    A class used to represent a Sensor.
    Attributes:
        pos: A x, y position tuple.
        state: The current state of the sensor.
        agent_type: What type of agent this is.
        sensor_id: The sensor id.
        start_pos: The x, y position that the sensor starts at.
        end_pos: The x, y position that the sensor ends at.
        lane_id: The lane id of where the sensor is.
        distance_from_light: The distance from the corresponding traffic light.
    """
    def __init__(
            self,
            unique_id: int,
            model: Model,
            pos: tuple,
            start_pos: tuple,
            end_pos: tuple,
            state: int,
            sensor_id: str,
            lane_id: str,
            distance_from_light: int,
            agent_type: str = "sensor"
    ):
        """
        Constructor for the Sensor class.
        :param unique_id: The unique agent ID.
        :param model: The model where the agent is in.
        :param pos: A x, y position tuple.
        :param start_pos: The x, y position that the sensor starts at.
        :param end_pos: The x, y position that the sensor ends at.
        :param state: The current state of the sensor.
        :param sensor_id: The sensor id.
        :param lane_id: The lane id of where the sensor is.
        :param distance_from_light: The distance from the corresponding traffic light.
        :param agent_type: What type of agent this is.
        """
        super().__init__(unique_id, model)
        self.pos = pos
        self.state = state
        self.agent_type = agent_type
        self.sensor_id = sensor_id
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.lane_id = lane_id
        self.distance_from_light = distance_from_light

    def car_on_sensor(self, threshold: int = 8) -> bool:
        """
        Function that checks if a car if on sensor.
        :param threshold: How much space between the center of the sensor and the car.
        :return: If there is a car on sensor: True, else False.
        """
        neighbors = self.model.space.get_neighbors(np.average(np.array([self.start_pos, self.end_pos]), axis=0), 10,
                                                   True)
        for car in neighbors:
            if car.agent_type == 'car':
                if car.active:
                    if math.dist(tuple(np.average(np.array([self.start_pos, self.end_pos]), axis=0)),
                                 car.pos) <= threshold and car.next_node.lane_id == self.lane_id:
                        self.model.sensor_on_car_found += 1
                        return True
        self.model.sensor_on_no_car += 1
        return False

    def step(self) -> None:
        """
        Mesa requires this function. Takes care of all the sensor logic.
        :return: None.
        """
        data_state = self.model.read_row_col(self.sensor_id)
        if data_state != "|":
            self.state = 0
        else:
            if self.sensor_id not in self.model.active_loops.keys():
                self.car_on_sensor()
            self.state = 1


class Light(Agent):
    """
    A class used to represent a Light.
    Attributes:
        pos: A x, y position tuple.
        state: The current state if the light.
        agent_type: What type of agent this is.
        light_id: The traffic light id.
    """
    def __init__(
            self,
            unique_id: int,
            model: Model,
            pos: tuple,
            state: int,
            light_id: str,
            agent_type: str = 'light'
    ):
        """
        Constructor for the Light class.
        :param unique_id: The unique agent ID.
        :param model: The model where the agent is in.
        :param pos: A x, y position tuple.
        :param state: The current state if the light.
        :param light_id: The traffic light id.
        :param agent_type: What type of agent this is.
        """
        super().__init__(unique_id, model)
        self.pos = pos
        self.state = state
        self.agent_type = agent_type
        self.light_id = light_id

    def step(self) -> None:
        """
        Mesa requires this function. Takes care of all the light logic.
        :return: None.
        """
        data_state = self.model.read_row_col(self.light_id)
        if data_state == '#':
            self.state = 2
        elif data_state == 'Z':
            self.state = 1
        else:
            self.state = 0
