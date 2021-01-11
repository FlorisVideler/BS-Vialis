from unittest import TestCase
from GitHub.traffic_model.traffic import agents
import math


class TestGet_next_point(TestCase):
    def test_get_next_point(self):
        distance = 1.0
        p1 = (0, 3)
        p3 = (4, 0)
        p2 = agents.get_next_point(p1, p3, 5, distance)[0]
        distance_calculated = math.sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))
        self.assertEqual(p2, (0.8, 2.4))
        self.assertEqual(distance, distance_calculated)
