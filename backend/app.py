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
import matplotlib.pyplot as plt
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

# valve_pins = app.config["VALVE_OUTPUTS"]
# setup_pins(valve_pins, GPIO.OUT)
# # input for sensors
# sensors_pins = app.config["SENSOR_INPUTS"]
# setup_pins(sensors_pins, GPIO.IN)

def camera_schedule():
  img_path = "/home/pi/garden_services/smart_irrigation/photos/garden.jpg"
  os.system("raspistill -o "+img_path)
  # img = send_file(img_path, mimetype='image/gif')
  # os.system("rm "+img_path)
  # return img

def open_valve():
  valve_pins = app.config["VALVE_OUTPUTS"]
  setup_pins(valve_pins, GPIO.OUT)
  GPIO.output(valve_pins[0], GPIO.HIGH)
  systi.sleep(60*app.config["VALVE_TIME"])
  GPIO.output(valve_pins[0], GPIO.LOW)
  return "Watered!"

def water_schedule():
  sensors_pins = app.config["SENSOR_INPUTS"]
  setup_pins(sensors_pins, GPIO.IN)
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
  
  ctr = 0
  for p in sensors_pins:
      # if soil is dry
      if GPIO.input(p):
          ctr += 1
  if not rain_level and ctr >= len(sensors_pins) /  2:
      print("Running water schedule!")
      open_valve()

def get_temperature():
    temperature = os.popen('vcgencmd measure_temp').read()
    temp_int = temperature[5:-3]
    return temp_int

def temperature_job():
    with open(f'temperature.txt', 'a') as f:
        f.write(get_temperature() + '\n')

sched = BackgroundScheduler(daemon=True)
#sched.add_job(water_schedule,'cron',hour='8, 18', minute=0, timezone="America/Chicago")
# sched.add_job(water_schedule,'interval',minutes=1)
sched.add_job(camera_schedule,'interval',minutes=60)
sched.add_job(temperature_job, 'interval', seconds=60)
sched.start()


def exit_cleanup():
  GPIO.cleanup()
  print("GPIO pins are cleaned up!")

atexit.register(exit_cleanup)

@app.route("/configs", methods=["POST"])
def GET_change_configs():
  updated_configs_raw = request.get_data().decode("utf-8")
  updated_configs = json.loads(updated_configs_raw, parse_int=int)
  for key in updated_configs:
    print(key+": "+updated_configs[key])
    if updated_configs[key]!="":
      if key=="SENSOR_INPUTS" or key=="VALVE_OUTPUTS":
        updated_configs[key] = [int(x) for x in updated_configs[key].split(" ")]
        print(updated_configs[key])
      else:
        updated_configs[key]= int(updated_configs[key])
    else:
      updated_configs[key]= int(app.config[key])
      print(type(updated_configs[key]))
  f = open("config.json", "w")
  f.write(json.dumps(updated_configs))
  f.close()
  return "success"

@app.route("/sensor", methods=["GET"])
def GET_sensor():
  sensors_pins = app.config["SENSOR_INPUTS"]
  setup_pins(sensors_pins, GPIO.IN)
  input_list = []
  for pin in sensors_pins:
    val = GPIO.input(pin)
    input_list.append(val)
  return str(input_list), 200

@app.route("/water", methods=["GET"])
def GET_water():
  msg = ""
  try:
    # valve_pins = app.config["VALVE_OUTPUTS"]
    # setup_pins(valve_pins, GPIO.OUT)
    # GPIO.output(valve_pins[0], GPIO.HIGH)
    # systi.sleep(10)
    open_valve()
    msg = "Success!"
  except:
    msg = "Failed!"
  print(msg)
  return msg

@app.route("/stop_water", methods=["GET"])
def GET_stop_water():
  msg = ""
  try:
    exit_cleanup()
    msg = "Success!"
  except:
    msg = "Failed!"
  print(msg)
  return msg
  
@app.route("/pi_temperature", methods=["GET"])
def GET_pi_temperature():
    temp_int = get_temperature()
    temp_json = json.dumps({"pi_temperature": temp_int})
    return temp_json

# @app.route("/temp_analysis", methods=['GET'])
def temp_analysis():
    temps = []
    with open('temperature.txt', "r") as f:
        for l in f:
            temps.append(float(l))
    x = [i for i in range(len(temps))]
    plt.plot(x, temps)
    plt.xlabel('Time Stamp')
    plt.ylabel('pi temperature')
    plt.title('Temperature of Raspberry Pi Over Time')
    plt.savefig('temperature_chart.png')

@app.route("/camera", methods=["GET"])
def GET_camera():
  img_path = "/home/pi/garden_services/smart_irrigation/photos/garden.jpg"
  os.system("raspistill -o "+img_path)
  img = send_file(img_path, mimetype='image/gif')
  os.system("rm "+img_path)
  return img, 200

@app.route('/chart', methods=["GET"])
def show_chart():
    temp_analysis()
    full_filename = "/home/pi/garden_services/smart_irrigation/backend/temperature_chart.png"
    img = send_file(full_filename, mimetype='image/gif')
    return img, 200