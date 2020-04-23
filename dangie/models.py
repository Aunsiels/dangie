from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField


class PlanForm(FlaskForm):

    functions = TextAreaField("Functions",
                              render_kw={"style":"width:100%; "
                                        "height: 10em;margin-bottom: 1em;"
                                                 "resize: vertical"})
    search = SubmitField("Find Plan")