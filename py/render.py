##  Begin Standard Imports
import os
from pathlib import Path
from flask import Flask, render_template

##  Begin Local Imports
import resources

app = Flask(__name__, template_folder=str(resources.CONST_FRONTEND_DIR))

@app.route("/")
def render_index():
    return render_template("index.html")