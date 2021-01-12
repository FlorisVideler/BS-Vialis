import unittest
from traffic_model.simulation import agents
from traffic_model.simulation.agents import Car, Node, Light
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
        testLight = Light(
            0,
            Traffic,
            (1, 1),
            False,
            "Light",)
        testNode1 = Node(
            0,
            Traffic,
            (1, 1),
            False,
            False,
            5,
            testLight,
        )
        testNode2=Node(
            0,
            Traffic,
            (2, 2),
            False,
            False,
            5,
            testLight,
        )
        testCar = Car(
                    0,
                 Traffic,
                    (1,1),
                    [testNode1,testNode2],
                    1,
                    testNode1,
                    testNode2,
                    testNode2)
        self.assertNotEqual(testCar.current_node, testCar.end_node, "Endnode == Current node, Fails because it cant move.")

    def test_red_light(self):
        testLight = Light(
            0,
            Traffic,  # Waarom geeft traffic een warning?!
            (1, 1),
            False,
            "Light",
        )
        testNode = Node(
            0,
            Traffic,
            (1, 1),
            False,
            False,
            5,
            testLight,
        )


        if testNode.stop_line != 1 and testLight.state != 1:
            p1 = 1
        else:
            p1 = 0
        self.assertEqual(1, p1, "Stopline and Lightstate are not both False.")

if __name__ == '__main__':
    unittest.main()
