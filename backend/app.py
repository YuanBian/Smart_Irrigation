# RUNNING ON PORT 5000
from flask import Flask, render_template, request, jsonify, send_file
import os
import requests
from datetime import datetime, timedelta, time
import time as systi
import re
from dotenv import load_dotenv
import datetime
import json
import RPi.GPIO as GPIO
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

app.config.from_file("config.json", load=json.load)

# set up pi GPIO
GPIO.setmode(GPIO.BCM)
# input_pin = 2
# GPIO.setup(input_pin, GPIO.IN)


# load env
load_dotenv()
WEATHER_API = os.getenv("WEATHER_API")

def setup_pins(pins, GPIO_TYPE):
  for pin in pins:
    GPIO.setup(pin, GPIO_TYPE)

valve_pins = app.config["VALVE_OUTPUTS"]
setup_pins(valve_pins, GPIO.OUT)
# input for sensors
sensors_pins = app.config["SENSOR_INPUTS"]
setup_pins(sensors_pins, GPIO.IN)

def camera_schedule():
  img_path = "/home/pi/garden_services/smart_irrigation/photos/garden.jpg"
  os.system("raspistill -o "+img_path)
  # img = send_file(img_path, mimetype='image/gif')
  # os.system("rm "+img_path)
  # return img

def open_valve():
  GPIO.output(valve_pins[0], GPIO.HIGH)
  systi.sleep(10)
  GPIO.output(valve_pins[0], GPIO.LOW)
  return "Watered!"

def water_schedule():
  weather_data = requests.get(
    WEATHER_API
  ).json()
  today_data = weather_data["daily"][0]
  rain_chance = today_data["pop"]
  rain_level = None
  try:
      rain_level = today_data["rain"]
  except:
      pass
  if rain_level:
      open_valve()


sched = BackgroundScheduler(daemon=True)
sched.add_job(water_schedule,'cron',hour='8, 18', minute=0, timezone="America/Chicago")
# sched.add_job(water_schedule,'interval',minutes=60)
sched.add_job(camera_schedule,'interval',minutes=60)

sched.start()


def exit():
  GPIO.cleanup()
  print("GPIO pins are cleaned up!")

atexit.register(exit)

@app.route("/configs", methods=["POST"])
def GET_change_configs():
  updated_configs = request.get_json(force=True)
  print(updated_configs)
  f = open("config.json", "w")
  f.write(json.dumps(updated_configs, indent=4))
  f.close()
  return request

@app.route("/sensor", methods=["GET"])
def GET_sensor():
  input_list = []
  for pin in sensors_pins:
    val = GPIO.input(pin)
    input_list.append(val)
  return str(input_list)

@app.route("/water", methods=["GET"])
def GET_water():
  msg = ""
  try:
    valve_pins = app.config["VALVE_OUTPUTS"]
    setup_pins(valve_pins, GPIO.OUT)
    # GPIO.output(valve_pins[0], GPIO.HIGH)
    msg = "Success!"
  except:
    msg = "Failed!"
  return msg
  
@app.route("/pi_temperature", methods=["GET"])
def GET_pi_temperature():
    temperature = os.popen('vcgencmd measure_temp').read()
    temp_int = temperature[5:-3]
    temp_json = json.dumps({"pi_temperature": temp_int})
    return temp_json

@app.route("/camera", methods=["GET"])
def GET_camera():
  img_path = "/home/pi/garden_services/smart_irrigation/photos/garden.jpg"
  os.system("raspistill -o "+img_path)
  img = send_file(img_path, mimetype='image/gif')
  os.system("rm "+img_path)
  return img
