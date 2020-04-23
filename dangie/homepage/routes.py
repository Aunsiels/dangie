import os

from flask import render_template, request

from dangie.demo import compute_plan
from dangie.homepage.blueprint import BP
from dangie.models import PlanForm


@BP.route("/", methods=["GET", "POST"])
def home():
    form = PlanForm()
    svg = None
    if form.validate_on_submit():
        row_functions = form.functions.data
        svg = compute_plan(row_functions)
    else:
        function_name = request.args.get('function_name', None, type=str)
        if (function_name is not None and "/" not in function_name and
                function_name.endswith(".txt") and
                function_name.count(".") == 1):
            path_to_function = \
                os.path.abspath(os.path.dirname(__file__)) + \
                "/../functions/" + function_name
            if os.path.exists(path_to_function):
                with open(path_to_function) as f:
                    form.functions.data = f.read()
    return render_template("index.html", form=form, svg=svg)
