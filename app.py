# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# -*- coding: utf-8 -*-

import logging
import os  # to remove temp files
import uuid  # to generate temporary filenames

from flask import Flask, render_template, redirect, url_for, session
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm, CSRFProtect
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.fields import SubmitField, TextAreaField
from google.cloud import vision
vision_client = vision.ImageAnnotatorClient()

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = "dev"

# set default button sytle and size, will be overwritten by macro parameters
app.config["BOOTSTRAP_BTN_STYLE"] = "primary"
app.config["BOOTSTRAP_BTN_SIZE"] = "sm"

bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)


class UploadForm(FlaskForm):
    """A basic form to upload a file and take a text prompt."""

    pdf_file = FileField(
        validators=[
            FileRequired(),
            FileAllowed(["jpg"], "Please select a JPG."),
        ],
        label="Select a JPG",
    )
    text_input = TextAreaField(label="Instructions", default="Summarize the JPG.")
    submit = SubmitField()


@app.route("/", methods=["GET", "POST"])
def index():
    """Route to display the input form and query the LLM."""
    form = UploadForm()
    if form.validate_on_submit():
        pdf_temp_filename = str(uuid.uuid4())
        form.pdf_file.data.save(pdf_temp_filename)
        image = vision.Image()
        image.source.image_uri = pdf_temp_filename

    # Safe search using Cloud-Vision-API
    response = vision_client.safe_search_detection(image=image)
    result = response.safe_search_annotation

    return render_template("index.html", upload_form=form)


@app.route("/pdf_results", methods=["GET", "POST"])
def pdf_results():
    """Route to display results."""

    # flash("Awaiting the model's response!")

    return render_template(
        "pdf_results.html", response_text=result
    )


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)
