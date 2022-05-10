from flask import Flask, render_template, request, jsonify
import os
import requests
from datetime import datetime, timedelta, time
import re
from dotenv import load_dotenv
import datetime
import json

load_dotenv()
WEATHER_API = os.getenv("WEATHER_API")

#  1. change configs
#  2. use sensors
#  3. open valve
#  4. measure Pi internal temperature

app = Flask(__name__)

app.config['TESTING'] = "10"


@app.route("/configs/<value>", methods=["GET"])
def GET_change_configs(value):
  app.config['TESTING'] = value
  return app.config['TESTING']

@app.route("/sensor", methods=["GET"])
def GET_sensor():
  return app.config['TESTING']

@app.route("/water", methods=["GET"])
def GET_water():
  return 0

@app.route("/pi_temperature", methods=["GET"])
def GET_pi_temperature():
  return 0
  
# @app.route("/change_config/<value>", methods=["GET"])
# def GET_weather():
#  config_f = open("/Users/yuanbian/Desktop/smart_irrigation/backend/config.json","r")
#  configs = json.load(config_f)
#  config_f.close()

#  valveTime = configs["valveTime"]
#  photoTimeInterval = configs["photoTimeInterval"]
#  moistureSensorCheckTime = configs["moistureSensorCheckTime"]
#  frostWarningThreshold = configs["frostWarningThreshold"]
#  emails = configs["emails"]

#  new_configs = {
#    "valveTime": valveTime,
#    "photoTimeInterval": photoTimeInterval,
#    "moistureSensorCheckTime": moistureSensorCheckTime,
#    "emails":emails,
#    "frostWarningThreshold": frostWarningThreshold
#  }

#  new_configs_str = json.dumps(new_configs)
#  new_config_f = open("/Users/yuanbian/Desktop/smart_irrigation/backend/config.json","w")
#  new_config_f.write(new_configs_str)
#  new_config_f.close()

#  return "current configs: "+new_configs_str
