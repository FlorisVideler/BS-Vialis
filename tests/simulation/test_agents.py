import unittest
from traffic_model.simulation import agents
from traffic_model.simulation.agents import Car, Node, Light, Sensor
from traffic_model.simulation.model import Traffic
import math

class TestAgents(unittest.TestCase):
    def test_get_next_point(self):
        distance = 1.0
        p1 = (0, 3)
        p3 = (4, 0)
        p2 = agents.get_next_point(p1, p3, 5, distance)[0]
        distance_calculated = math.sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))
        self.assertEqual(p2, (0.8, 2.4))
        self.assertEqual(distance, distance_calculated)

    def test_get_next_node(self):
        test_light = Light(0, Traffic(), (1, 1), False, "Light")
        test_node1 = Node(0, Traffic(), (1, 1), False, False, 5, test_light)
        test_node2 = Node(0, Traffic(), (2, 2), False, False, 5, test_light)
        test_car = Car(0, Traffic(), (1, 1), [test_node1, test_node2], 1, test_node1, test_node2, test_node2)
        self.assertNotEqual(test_car.current_node, test_car.end_node,
                            "Endnode == Current node, Fails because it cant move.")

    def test_red_light(self):
        test_light = Light(0, Traffic(), (1, 1), False, "Light")
        test_node = Node(0, Traffic(), (1, 1), False, False, 5, test_light)

        if test_node.stop_line != 1 and test_light.state != 1:
            p1 = 1
        else:
            p1 = 0
        self.assertEqual(1, p1, "Stopline and Lightstate are not both False.")

    def test_get_light_from_lane(self):
        test_model = Traffic()
        test_sensor = Sensor(0, test_model, (1, 1), (0, 1), (2, 1), 0, "Twenty", "1", 1)
        test_model.lanes = test_model.make_intersection()
        self.assertEqual(test_sensor.get_light_from_lane(), test_model.lanes['1']['in']['nodes'][0].light)

    def test_get_light_from_lane_no_light(self):
        test_model = Traffic()
        test_sensor = Sensor(0, test_model, (1, 1), (0, 1), (2, 1), 0, "Twenty", "15", 1)
        test_model.lanes = test_model.make_intersection()
        self.assertEqual(test_sensor.get_light_from_lane(), None)


if __name__ == '__main__':
    unittest.main()
