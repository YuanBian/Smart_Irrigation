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

load_dotenv()
WEATHER_API = os.getenv("WEATHER_API")
IMG_PATH = os.getenv("IMG_PATH")
CHART_PATH = os.getenv("CHART_PATH")


def setup_pins(pins, GPIO_TYPE):
    for pin in pins:
        GPIO.setup(pin, GPIO_TYPE)


def camera_schedule():
    os.system("raspistill -o " + IMG_PATH)


def open_valve():

    valve_pins = app.config["VALVE_OUTPUTS"]
    setup_pins(valve_pins, GPIO.OUT)
    GPIO.output(valve_pins[0], GPIO.HIGH)
    systi.sleep(60 * app.config["VALVE_TIME"])
    GPIO.output(valve_pins[0], GPIO.LOW)
    return "Watered!"


def get_current_time():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt_string


def water_schedule():
    sensors_pins = app.config["SENSOR_INPUTS"]
    setup_pins(sensors_pins, GPIO.IN)
    weather_data = requests.get(WEATHER_API).json()
    today_data = weather_data["daily"][0]
    rain_chance = today_data["pop"]
    rain_level = None
    try:
        rain_level = today_data["rain"]
    except:
        pass

    if not rain_level:
        with open(f"water_schedule.txt", "a") as f:
            f.write(
                get_current_time
                + ": Running water schedule for "
                + str(app.config["VALVE_TIME"])
                + " minutes!"
            )
        print("Running water schedule!")
        open_valve()


def get_temperature():
    temperature = os.popen("vcgencmd measure_temp").read()
    temp_int = temperature[5:-3]
    return temp_int


def temperature_job():
    with open(f"temperature.txt", "a") as f:
        f.write(get_temperature() + "\n")


sched = BackgroundScheduler(daemon=True)
sched.add_job(water_schedule, "cron", hour="8,18", minute=0, timezone="America/Chicago")
sched.add_job(temperature_job, "interval", seconds=60)
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
        if updated_configs[key] != "":
            print()
            if key == "SENSOR_INPUTS" or key == "VALVE_OUTPUTS":
                updated_configs[key] = [int(x) for x in updated_configs[key].split(" ")]
                print(updated_configs[key])
            else:
                updated_configs[key] = int(updated_configs[key])
        else:
            if key == "SENSOR_INPUTS" or key == "VALVE_OUTPUTS":
                updated_configs[key] = app.config[key]
            else:
                updated_configs[key] = int(app.config[key])
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
    code = 200
    try:
        open_valve()
        print("WATERING NOW!")
        msg = "Success! Watering Now!"
    except:
        msg = "Failed!"
        code = 500
    print(msg)
    return msg, code


@app.route("/stop_water", methods=["GET"])
def GET_stop_water():
    msg = ""
    try:
        valve_pins = app.config["VALVE_OUTPUTS"]
        setup_pins(valve_pins, GPIO.OUT)
        GPIO.output(valve_pins[0], GPIO.LOW)
        msg = "Success! Water stopped"
    except:
        msg = "Failed!"
    print(msg)
    return msg


@app.route("/pi_temperature", methods=["GET"])
def GET_pi_temperature():
    temp_int = get_temperature()
    temp_json = json.dumps({"pi_temperature": temp_int})
    return temp_json


def temp_analysis():
    temps = []
    with open("temperature.txt", "r") as f:
        for l in f:
            temps.append(float(l))
    x = [i for i in range(len(temps))]
    plt.plot(x, temps)
    plt.xlabel("Time Stamp")
    plt.ylabel("pi temperature")
    plt.title("Temperature of Raspberry Pi Over Time")
    plt.savefig("temperature_chart.png")


@app.route("/camera", methods=["GET"])
def GET_camera():
    img_path = CHART_PATH + "/garden.jpg"
    os.system("raspistill -o " + img_path)
    img = send_file(img_path, mimetype="image/gif")
    os.system("rm " + img_path)
    return img, 200


@app.route("/chart", methods=["GET"])
def show_chart():
    temp_analysis()
    full_filename = CHART_PATH
    img = send_file(full_filename, mimetype="image/gif")
    return img, 200
