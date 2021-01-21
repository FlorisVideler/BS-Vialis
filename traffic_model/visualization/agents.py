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

    Attributes:
        next_pos: The next position the car wants to move to. X, y tuple.
        active: Whether the car is active or not.
        pos: A x, y position tuple.
        agent_type: What type of agent this is.
        index: The index of the data.
        next_pos: The next x, y coordinate the car is moving to.
        dist: The distance to the next position.
        speed: The speed the car moves at.
    """

    def __init__(self,
                 unique_id: int,
                 model,
                 pos,
                 geo_data,
                 index: int = 1,
                 active: bool = True,
                 agent_type: str = "car"
                 ):
        """
        Constructor for the Car class.
        :param unique_id: The unique agent ID.
        :param model: The model where the agent is in.
        :param pos: A x, y position tuple.
        :param geo_data: The data used to drive the car.
        :param index: The index of the data.
        :param active: Whether the car is active or not.
        :param agent_type: What type of agent this is.
        """
        super().__init__(unique_id, model)
        self.geo_data = geo_data
        self.active = active
        self.agent_type = agent_type
        self.pos = pos
        self.index = index
        self.next_pos = self.geo_data[self.index][0] * self.model.space.x_max, self.geo_data[self.index][
            1] * self.model.space.y_max
        self.dist = abs(math.dist(self.pos, self.next_pos))
        self.speed = self.dist / 10

    def step(self) -> None:
        """
        A function that Mesa requires, takes care of all the car logic.
        :return: None
        """
        try:
            next_pos, next_distance_to_next_node = get_next_point(self.pos, self.next_pos, self.dist, self.speed)
            if next_distance_to_next_node <= 0:
                self.index += 1
                self.pos = self.next_pos
                self.next_pos = self.geo_data[self.index][0] * self.model.space.x_max, self.geo_data[self.index][
                    1] * self.model.space.y_max
                self.dist = abs(math.dist(self.pos, self.next_pos))
                self.speed = self.dist / 10
                next_pos, next_distance_to_next_node = get_next_point(self.pos, self.next_pos, self.dist, self.speed)
                self.speed = next_distance_to_next_node / 10
            self.pos = next_pos
            self.dist = next_distance_to_next_node
        except IndexError:
            print('Car is done')


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
            model,
            start_node: Node,
            end_node: Node,
            lane_id: str,
            light = None,
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
        intersection_id: The id of the intersection the sensor is on.
    """
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
        :param intersection_id: The id of the intersection the sensor is on.
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
        self.intersection_id = intersection_id

    def step(self) -> None:
        """
        Mesa requires this function. Takes care of all the sensor logic.
        :return: None.
        """
        data_state = self.model.read_row_col(self.intersection_id, self.sensor_id)
        if data_state != "|":
            self.state = 0
        else:
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
            model,
            pos: tuple,
            state: int,
            light_id: str,
            intersection_id: str,
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
        self.intersection_id = intersection_id

    def step(self) -> None:
        """
        Mesa requires this function. Takes care of all the light logic.
        :return: None.
        """
        data_state = self.model.read_row_col(self.intersection_id, self.light_id)
        if data_state == '#':
            self.state = 2
        elif data_state == 'Z':
            self.state = 1
        else:
            self.state = 0
