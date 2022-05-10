from flask import Flask, render_template, request, jsonify
import os
import requests
from datetime import datetime, timedelta, time
import re
from dotenv import load_dotenv
import datetime

load_dotenv()
WEATHER_API = os.getenv("WEATHER_API")

app = Flask(__name__)

# render frontend
# @app.route("/", methods=["GET"])
# def GET_watch():
#     return 0

# show current view of garden
@app.route("/watch", methods=["GET"])
def GET_watch():
    return 0

# edit configs
@app.route("/configs", methods=["GET"])
def GET_change_configs():
    return 0

# water now
@app.route("/waterNow", methods=["GET"])
def GET_waterNow():
    return 0

# use sensor now
@app.route("/sensor", methods=["GET"])
def GET_sensor():
    return 0

# get pi temperature
@app.route("/pi_temperature", methods=["GET"])
def GET_pi_temperature():
    return 0

# analysis
@app.route("/analysis/<mode>", methods=["GET"])
def GET_analysis(mode):
    return 0

