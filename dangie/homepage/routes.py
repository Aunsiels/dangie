import os
import random
import re
import string

from flask import render_template, request

from dangie.demo import compute_plan
from dangie.homepage.blueprint import BP
from dangie.models import PlanForm

REGEX = re.compile(r'(<ellipse fill=")(none)("[^>]*>\n<text[^>]*>[^LBS])')


@BP.route("/", methods=["GET", "POST"])
def home():
    form = PlanForm()
    svg = None
    name = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    svg_parse_tree = None
    message = ""
    if form.validate_on_submit():
        row_functions = form.functions.data
        svg = compute_plan(row_functions, name)
        if os.path.exists(name + ".svg"):
            with open(name + ".svg") as f:
                svg_parse_tree = f.read()
                svg_parse_tree = REGEX.sub(r'\1green\3', svg_parse_tree)
            os.system("rm " + name + ".svg")
        else:
            message = "No Equivalent Rewriting Found."
    else:
        function_name = request.args.get('function_name', "singer.txt",
                                         type=str)
        if (function_name is not None and "/" not in function_name and
                function_name.endswith(".txt") and
                function_name.count(".") == 1):
            path_to_function = \
                os.path.abspath(os.path.dirname(__file__)) + \
                "/../functions/" + function_name
            if os.path.exists(path_to_function):
                with open(path_to_function) as f:
                    form.functions.data = f.read()
    return render_template("index.html",
                           form=form,
                           svg=svg,
                           svg_parse_tree=svg_parse_tree,
                           message=message)
