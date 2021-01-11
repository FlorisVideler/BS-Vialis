from mesa.visualization.ModularVisualization import ModularServer

from .model import BoidFlockers
from .SimpleContinuousModule import SimpleCanvas
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement


class TimeText(TextElement):
    """
    Display a text count of how many happy agents there are.
    """

    def __init__(self):
        pass

    def render(self, model):
        return "Time: " + model.data_time


def boid_draw(agent):
    if agent.agent_type == "node":
        if agent.reg:
            if agent.light.state == 0:
                return {"Shape": "rect", "Filled": "true", "Color": "rgba(102, 178, 118, 0)", "w": 2, "h": 2}
            elif agent.light.state == 1:
                return {"Shape": "rect", "Filled": "true", "Color": "Orange", "w": 2, "h": 2}
            else:
                return {"Shape": "rect", "Filled": "true", "Color": "Green", "w": 2, "h": 2}
            return {"Shape": "rect", "Filled": "true", "Color": "Green", "w": 2, "h": 2}
        else:
            return {"Shape": "rect", "Filled": "true", "Color": "Red", "w": 2, "h": 2}
    if agent.agent_type == "sensor":
        if agent.state == 0:
            return {"Shape": "line", "Filled": "true", "Color": "rgba(0, 0, 255, 0.5)", "x1": agent.start_pos[0],
                    "y1": agent.start_pos[1], "x2": agent.end_pos[0], "y2": agent.end_pos[1]}
        if agent.state == 1:
            return {"Shape": "line", "Filled": "true", "Color": "#0000FF", "x1": agent.start_pos[0],
                    "y1": agent.start_pos[1], "x2": agent.end_pos[0], "y2": agent.end_pos[1]}
        # if agent.state == 0:
        #     return {"Shape": "rect", "Color": "Blue", "w": 6, "h": 6}
        # if agent.state == 1:
        #     return {"Shape": "rect", "Filled": "true", "Color": "Blue", "w": 6, "h": 6}
    if agent.agent_type == "road":
        if "reg" in agent.lane_id:
            if agent.light is None:
                return {"Shape": "line", "Filled": "true", "Color": "Red", "x1": agent.start_node.pos[0],
                        "y1": agent.start_node.pos[1], "x2": agent.end_node.pos[0], "y2": agent.end_node.pos[1]}
            if agent.light.state == 0:
                return {"Shape": "line", "Filled": "true", "Color": "rgba(102, 178, 118, 0)", "x1": agent.start_node.pos[0],
                        "y1": agent.start_node.pos[1], "x2": agent.end_node.pos[0], "y2": agent.end_node.pos[1]}
            elif agent.light.state == 1:
                return {"Shape": "line", "Filled": "true", "Color": "Orange", "x1": agent.start_node.pos[0],
                        "y1": agent.start_node.pos[1], "x2": agent.end_node.pos[0], "y2": agent.end_node.pos[1]}
            else:
                return {"Shape": "line", "Filled": "true", "Color": "Green", "x1": agent.start_node.pos[0],
                        "y1": agent.start_node.pos[1], "x2": agent.end_node.pos[0], "y2": agent.end_node.pos[1]}
        else:
            return {"Shape": "line", "Filled": "true", "Color": "rgba(0, 0, 0, 0.5)", "x1": agent.start_node.pos[0],
                    "y1": agent.start_node.pos[1], "x2": agent.end_node.pos[0], "y2": agent.end_node.pos[1]}
    if agent.agent_type == "light":
        if agent.state == 2:
            return {"Shape": "rect", "Filled": "true", "Color": "Green", "w": 8, "h": 8}
        elif agent.state == 1:
            return {"Shape": "rect", "Filled": "true", "Color": "Orange", "w": 8, "h": 8}
        else:
            return {"Shape": "rect", "Filled": "true", "Color": "Red", "w": 8, "h": 8}
    return {"Shape": "rect", "Filled": "true", "Color": "Pink", "w": 8, "h": 8}


boid_canvas = SimpleCanvas(boid_draw, 900, 900)
time_text_element = TimeText()
model_params = {
    "population": 100,
    "width": 900,
    "height": 900,
}

server = ModularServer(BoidFlockers, [boid_canvas, time_text_element], "Boids", model_params)
