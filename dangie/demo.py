# Animates an execution plan of functions
#
# Prerequisites:
# - Python 3
# - Python library pyformlang. Run "pip3 install pyformlang" in a terminal

from dangie.function import Function
from dangie.solver import Solver
import os

# Parameters of the layout
EDGELENGTH = 80
FONTSIZE = 10
STROKEWIDTH = 1
COLORS = ["blue", "orange", "green", "purple", "darkblue", "magenta",
          "saddlebrown", "teal", "deepskyblue", "indigo", "cornflowerblue",
          "darkred", "darkgoldenrod", "mediumvioletred", "violet"]

# Position of the list of function definitions
FUNCTIONX = FONTSIZE * 15
FUNCTIONSY = FONTSIZE * 2
SPEED = 1


class SVGPlanWriter:

    def __init__(self, functions_as_text, name="latest"):
        self.x = 0
        self.y = 0
        self.direction = 0
        self.forward = 1
        self.functions = None
        self.query = None
        self.result = ""
        self.max_x = 0
        self.max_y = 0
        self.min_x = 0
        self.min_y = 0
        self.load_functions(functions_as_text)
        self.name = name

    def load_functions(self, functions_as_text):
        functions = {}
        for line in functions_as_text.splitlines():
            line = line.strip()
            if len(line) == 0 or line[0] == "#" or line.index(":") == -1:
                continue
            line = line.replace(" ", "")
            functions[line.split(":")[0]] = {}
            functions[line.split(":")[0]]["path"] = line.split(":")[
                1].split(",")
        query = functions.pop("query", None)
        if query is None or len(query) != 1:
            self.functions = None
            self.query = "Need a query definition of the form 'query : " \
                         "relation'"
        else:
            self.functions = functions
            self.query = query["path"][0]

    # Produces the SVG file for a function definition file
    def run(self):
        self.result = ""
        if self.functions is None:
            return self.query
        plan, solver = self.make_plan()
        self.save_svg(plan)
        return self.result.replace("MAXX", str(self.max_x + 20 - self.min_x)) \
            .replace("MAXY", str(self.max_y + 10)) \
            .replace("MINX", str(self.min_x - 10)) \
            .replace("MINY", str(0)), solver

    def make_plan(self):
        read_functions = []
        for function in self.functions:
            read_function = Function(function)
            read_function.set_input_variable("x0")
            counter = 0
            for relation in self.functions[function]["path"]:
                if relation == "*":
                    read_function.set_existential_variable(
                        "x" + str(counter))
                    continue
                read_function.add_atom(relation, "x" + str(counter),
                                       "x" + str(counter + 1))
                counter += 1
            read_functions.append(read_function)
        solver = Solver(read_functions)
        return solver.solve(self.query, filename=self.name), solver

    # Creates the SVG file
    def save_svg(self, plan):
        self.write_svg_headers()
        self.write_functions()
        self.x = EDGELENGTH
        self.y += EDGELENGTH + FONTSIZE * 2
        self.direction = 0
        self.forward = 1
        if plan is None:
            self.result += (
                    "<text x='" + str(self.x) + "' y='" + str(self.y) +
                    "' font-size='" + str(FONTSIZE) + "'>No plan</text>")
            self.result += "</svg>"
        else:
            self.write_plan(plan)
            self.result += "</svg>"

    def write_svg_headers(self):
        self.result += (
            "<svg xmlns='http://www.w3.org/2000/svg' "
            "xmlns:xlink='http://www.w3.org/1999/xlink' "
            "preserveAspectRatio= 'xMidYMin meet' viewBox='MINX MINY MAXX "
            "MAXY'> ")
        self.result += "<defs>"
        for color in COLORS + ["red"]:
            self.result += (
                    "  <marker id='arrow" + color +
                    "' markerHeight='6' markerUnits='strokeWidth' "
                    "markerWidth='8' orient='auto' refX='0' refY='5' "
                    "viewBox='0 0 10 10'> <path d='M 0 0 L 10 5 L 0 10 z' "
                    "fill='" + color + "' stroke='" + color + "'/> </marker>")
            self.result += (
                    "  <marker id='box" + color +
                    "' markerHeight='6' "
                    "markerUnits='strokeWidth' "
                    "markerWidth='8' orient='auto' refX='0' refY='5' "
                    "viewBox='0 "
                    "0 10 10'> <path d='M 0 0 L 10 5 L 0 10 z' fill='none' "
                    "stroke='" + color + "'/> </marker>")
        self.result += "</defs>"

    def write_functions(self):
        counter = 0
        for f in self.functions:
            function = self.functions[f]
            self.y = FUNCTIONSY + FONTSIZE * 3 * counter
            function["index"] = counter
            function["color"] = COLORS[counter % len(COLORS)]
            self.result += (
                    "<text x='0' y='" + str(self.y) + "' fill='" +
                    function["color"] + "' font-size='" +
                    str(FONTSIZE) + "'>" +
                    f + "</text>")
            self.x = FUNCTIONX
            self.direction = 0
            self.forward = 1
            counter += 1
            i = 0
            for edge in function["path"]:
                if function["path"][i] == "*":
                    i += 1
                    continue
                self.write_edge(
                    edge,
                    function["color"],
                    is_existential=(i + 1 < len(function["path"]) and
                                    function["path"][i + 1] == "*"))
                i += 1

    # Prints a single edge. <isExistential> makes the arrow head empty.
    def write_edge(self, relation, color, is_existential=False):
        x2 = self.x
        finalx2 = self.x
        y2 = self.y
        finaly2 = self.y
        shift = str(-STROKEWIDTH * 3)
        if self.direction == 0:
            x2 += EDGELENGTH - 8
            finalx2 += EDGELENGTH
            trafo = "translate(0 " + shift + ")"
        elif self.direction == 1:
            y2 += EDGELENGTH - 8
            finaly2 += EDGELENGTH
            trafo = "rotate(90 " + str(self.x) + " " + str(
                self.y) + ") translate(0 " + shift + ")"
        elif self.direction == 2:
            x2 -= EDGELENGTH - 8
            finalx2 -= EDGELENGTH
            trafo = "translate(-" + str(EDGELENGTH) + " " + shift + ")"
        elif self.direction == 3:
            y2 -= EDGELENGTH - 8
            finaly2 -= EDGELENGTH
            trafo = "rotate(-90 " + str(self.x) + " " + str(
                self.y) + ") translate(0 " + shift + ")"
        else:
            trafo = ""
        self.max_x = max(self.max_x, self.x)
        self.max_x = max(self.max_x, x2)
        self.max_y = max(self.max_y, self.y)
        self.max_y = max(self.max_y, y2)
        self.min_x = min(self.min_x, self.x)
        self.min_x = min(self.min_x, x2)
        self.min_y = min(self.min_y, self.y)
        self.min_y = min(self.min_y, y2)
        self.result += (
                "<line x1='" + str(self.x) + "' y1='" + str(self.y) + "' x2='"
                + str(x2) + "' y2='" + str(y2) + "' stroke='" + color +
                "' stroke-width='" + str(STROKEWIDTH) + "' marker-end='url(#" +
                ("box" if is_existential else "arrow") + color + ")' />")
        self.result += ("<text x='" + str(self.x + FONTSIZE) + "' y='"
                        + str(self.y) + "' transform='" +
                        trafo + "' fill='" + color + "' font-size='" +
                        str(FONTSIZE) + "'>" + relation + "</text>")
        self.y = finaly2
        self.x = finalx2

    # Prints a plan (as a sequence of functions)
    def write_plan(self, plan):
        relations_printed_so_far = []
        directions_so_far = []
        self.result += ("<text x='" + str(self.x) + "' y='" + str(
            self.y + FONTSIZE) + "' fill='red' font-size='" + str(
            FONTSIZE) + "'>IN</text>")
        self.x += FONTSIZE * 2
        for i in range(0, len(plan)):
            self.write_function(relations_printed_so_far,
                                directions_so_far,
                                plan[i],
                                i,
                                i == len(plan) - 1)

    # Prints a function. Keeps track of previous relations in
    # <relationsPrintedSoFar>
    # and of their directions in <directionsSoFar>.
    # <index> is the position of the function in the plan.
    def write_function(self, relations_printed_so_far, directions_so_far,
                       function_name, index, is_last):
        limit = 1000
        if function_name[-2] == '#':
            limit = int(function_name[-1]) - int('0')
            function_name = function_name[0:-2]
        function = self.functions[function_name]
        self.max_x = max(self.max_x, FUNCTIONX + len(function["path"]) *
                         EDGELENGTH / 2 - self.x)
        self.max_y = max(self.max_y, FUNCTIONSY + FONTSIZE * 3 *
                         function["index"] - self.y)
        self.min_x = min(self.min_x, FUNCTIONX + len(function["path"]) *
                         EDGELENGTH / 2 - self.x)
        self.min_y = min(self.min_y, FUNCTIONSY + FONTSIZE * 3 *
                         function["index"] - self.y)
        self.result += "<g transform='translate(-1000 -1000)'>"
        self.result += (
                "<animateTransform attributeName='transform'	 "
                "type='translate'" +
                "	 from='" + str(
            FUNCTIONX + len(function["path"]) * EDGELENGTH / 2 - self.x) +
                " " + str(
            FUNCTIONSY + FONTSIZE * 3 * function["index"] - self.y) +
                "' to='0 0' begin='" + str(
            index * 2 / SPEED + 3 / SPEED) +
                "s' dur='" + str(1 / SPEED) + "s' fill='freeze' />")
        last_x = self.x
        last_y = self.y
        last_relation = ""
        for i in range(0, len(function["path"])):
            if function["path"][i] == "*":
                continue
            last_x = self.x
            last_y = self.y
            last_relation = function["path"][i]
            self.add_edge(relations_printed_so_far, directions_so_far,
                          function["path"][i],
                          function["color"],
                          is_existential=(i + 1 < len(function["path"]) and
                                          function["path"][i + 1] == "*"))
            limit -= 1
            if limit == 0:
                break
        self.result += "</g>"
        if is_last:
            self.x = last_x
            self.y = last_y
            self.write_edge(last_relation, "red")

    # Adds an edge to the current diagram. Keeps track of previous relations
    # in <relationsPrintedSoFar>
    # and of their directions in <directionsSoFar>.
    # <isExistential> will draw an empty arrow head.
    def add_edge(self, relations_printed_so_far, directions_so_far,
                 relation, color, is_existential=False):
        is_same = (len(relations_printed_so_far) > 0 and
                   relations_printed_so_far[-1] == inverse(relation))
        if self.forward == 1 and is_same:
            self.direction = (directions_so_far[-1] + 2) % 4
            del relations_printed_so_far[-1]
            del directions_so_far[-1]
            self.change_direction()
            self.forward = 0
        elif self.forward == 0 and not is_same:
            self.direction = (self.direction + 3) % 4
            self.forward = 1
            relations_printed_so_far.append(relation)
            directions_so_far.append(self.direction)
        elif self.forward == 0 and is_same:
            del relations_printed_so_far[-1]
            self.direction = (directions_so_far[-1] + 2) % 4
            del directions_so_far[-1]
        elif self.forward == 1 and not is_same:
            relations_printed_so_far.append(relation)
            directions_so_far.append(self.direction)
        self.write_edge(relation, color, is_existential)

    # Adjusts the global coordinates after a change of direction
    def change_direction(self):
        if self.direction == 0:
            self.y -= 2 * FONTSIZE
        elif self.direction == 1:
            self.x += 2 * FONTSIZE
        elif self.direction == 2:
            self.y += 2 * FONTSIZE
        elif self.direction == 3:
            self.x -= 2 * FONTSIZE


# Returns the inverse of a relation
def inverse(relation):
    return relation[:-1] if relation[-1] == '-' else relation + '-'


def compute_plan(functions, name="latest"):
    svg_plan_writer = SVGPlanWriter(functions, name)
    return svg_plan_writer.run()
