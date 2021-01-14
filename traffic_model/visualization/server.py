from mesa.visualization.ModularVisualization import ModularServer

from .model import Traffic
from .SimpleContinuousModule import SimpleCanvas
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter



class TimeText(TextElement):
    """
    Display a text count of how many happy agents there are.
    """

    def __init__(self):
        pass

    def render(self, model):
        return "Time: " + model.data_time


def draw(agent):
    if agent.agent_type == "node":
        return draw_node(agent)
    if agent.agent_type == "sensor":
        return draw_sensor(agent)
    if agent.agent_type == "road":
        return draw_road(agent)
    if agent.agent_type == "light":
        return draw_light(agent)
    if agent.agent_type == "car":
        return draw_car(agent)
    return {"Shape": "rect", "Filled": "true", "Color": "Cyan", "w": 8, "h": 8}


def draw_car(car):
    if car.active:
        return {"Shape": "rect", "Filled": "true", "Color": "Black", "w": 6, "h": 6}
    else:
        return {}


def draw_sensor(sensor):
    if sensor.state == 0:
        return {"Shape": "line", "Filled": "true", "Color": "rgba(0, 0, 255, 0.5)", "x1": sensor.start_pos[0],
                "y1": sensor.start_pos[1], "x2": sensor.end_pos[0], "y2": sensor.end_pos[1], "Type": sensor.agent_type}
    if sensor.state == 1:
        return {"Shape": "line", "Filled": "true", "Color": "#0000FF", "x1": sensor.start_pos[0],
                "y1": sensor.start_pos[1], "x2": sensor.end_pos[0], "y2": sensor.end_pos[1], "Type": sensor.agent_type}


def draw_road(road):
    if "reg" in road.lane_id:
        if road.light is None:
            return {"Shape": "line", "Filled": "true", "Color": "Red", "x1": road.start_node.pos[0],
                    "y1": road.start_node.pos[1], "x2": road.end_node.pos[0], "y2": road.end_node.pos[1], "Type": road.agent_type}
        if road.light.state == 0:
            return {"Shape": "line", "Filled": "true", "Color": "rgba(102, 178, 118, 0)", "x1": road.start_node.pos[0],
                    "y1": road.start_node.pos[1], "x2": road.end_node.pos[0], "y2": road.end_node.pos[1], "Type": road.agent_type}
        elif road.light.state == 1:
            return {"Shape": "line", "Filled": "true", "Color": "Orange", "x1": road.start_node.pos[0],
                    "y1": road.start_node.pos[1], "x2": road.end_node.pos[0], "y2": road.end_node.pos[1], "Type": road.agent_type}
        else:
            return {"Shape": "line", "Filled": "true", "Color": "Green", "x1": road.start_node.pos[0],
                    "y1": road.start_node.pos[1], "x2": road.end_node.pos[0], "y2": road.end_node.pos[1], "Type": road.agent_type}
    else:
        return {"Shape": "line", "Filled": "true", "Color": "rgba(0, 0, 0, 0.5)", "x1": road.start_node.pos[0],
                "y1": road.start_node.pos[1], "x2": road.end_node.pos[0], "y2": road.end_node.pos[1], "Type": road.agent_type}


def draw_node(node):
    if node.reg:
        if node.light.state == 0:
            return {"Shape": "rect", "Filled": "true", "Color": "rgba(102, 178, 118, 0)", "w": 2, "h": 2}
        elif node.light.state == 1:
            return {"Shape": "rect", "Filled": "true", "Color": "Orange", "w": 2, "h": 2}
        else:
            return {"Shape": "rect", "Filled": "true", "Color": "Green", "w": 2, "h": 2}
    else:
        return {"Shape": "rect", "Filled": "true", "Color": "Red", "w": 2, "h": 2}


def draw_light(light):
    if light.state == 2:
        return {"Shape": "rect", "Filled": "true", "Color": "Green", "w": 8, "h": 8}
    elif light.state == 1:
        return {"Shape": "rect", "Filled": "true", "Color": "Orange", "w": 8, "h": 8}
    else:
        return {"Shape": "rect", "Filled": "true", "Color": "Red", "w": 8, "h": 8}


traffic_canvas = SimpleCanvas(draw, 750, 750)
time_text_element = TimeText()
model_params = {
    "route": UserSettableParameter(
        "choice",
        "Route",
        value=0,
        choices=list(Traffic.route_dict.keys()),
    ),
    "width": 750,
    "height": 750,
}

server = ModularServer(Traffic, [traffic_canvas, time_text_element], "Traffic", model_params)
