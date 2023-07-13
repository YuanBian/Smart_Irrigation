from flask import Flask, render_template, request, jsonify
import os
import requests
from datetime import datetime, timedelta, time
import re
from dotenv import load_dotenv
from datetime import datetime
import json
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import smtplib
from apscheduler.schedulers.background import BackgroundScheduler

# load weather API
load_dotenv()
WEATHER_API = os.getenv("WEATHER_API")
APP_PASSWORD = os.getenv("APP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")
TO_EMAIL = os.getenv("TO_EMAIL")


def alerts_getter():
    """Return a warning message if any anomaly is detected"""
    general_alerts = ""
    frost_warning = ""
    default_no_warning = general_alerts + frost_warning
    weather_data = requests.get(WEATHER_API).json()
    try:
        general_alerts = json.dumps(weather_data["alerts"])
    except:
        pass
    # check temp for the next week
    min_temp = kelvinToCelsius(weather_data["daily"][1]["temp"]["min"])
    if min_temp <= 2:
        frost_warning = "There is frost tomorrow! "
    msg_text = general_alerts + frost_warning
    return msg_text


def send_email():
    """Send an email if there is an alert"""
    alerts = alerts_getter()
    if alerts != "":
        smtp = smtplib.SMTP("smtp.gmail.com", 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(FROM_EMAIL, APP_PASSWORD)
        msg = MIMEMultipart()
        msg["Subject"] = "Weather Warning"
        msg.attach(MIMEText(alerts))
        to = [TO_EMAIL]
        smtp.sendmail(from_addr=FROM_EMAIL, to_addrs=to, msg=msg.as_string())
        smtp.quit()


# schedule a job to send email at 8 am every morning
sched = BackgroundScheduler()
sched.add_job(send_email, "cron", hour=8, minute=0, timezone="America/Chicago")
sched.start()


app = Flask(__name__)

# render frontend
@app.route("/admin_page", methods=["GET"])
def GET_admin_page():
    return render_template("admin_page.html")


# show current view of garden
@app.route("/watch", methods=["GET"])
def GET_watch():
    return request.data


# edit configs
@app.route("/configs", methods=["POST"])
def GET_change_configs():
    updated_configs = dict(request.form)
    print(updated_configs)
    res = requests.post(
        "http://127.0.0.1:5000/configs", data=json.dumps(updated_configs)
    )
    return "Status code: " + str(res.status_code)


# water now
@app.route("/water_now", methods=["GET"])
def GET_waterNow():
    res = requests.get("http://192.168.1.38:5000/water")
    return "Status code: " + str(res.status_code)


@app.route("/stop_water", methods=["GET"])
def GET_stop_water():
    res = requests.get("http://192.168.1.38:5000/stop_water")
    return "Status code: " + str(res.status_code)


# use sensor now
@app.route("/get_sensor_now", methods=["GET"])
def GET_sensor():
    res = requests.get("http://127.0.0.1:5000/sensor").json()
    return "Sensor data: " + str(res)


# get pi temperature
@app.route("/pi_temperature", methods=["GET"])
def GET_pi_temperature():
    r = requests.get("http://127.0.0.1:5000/pi_temperature").json()
    return r["pi_temperature"]


@app.route("/weather", methods=["GET"])
def GET_weather():
    weather_data = requests.get(WEATHER_API).json()
    return json.dumps(weather_data["daily"][0])


def kelvinToCelsius(kelvin):
    return kelvin - 273.15


# get alerts from weather api
# additional feature: send "Frost Warning" alert when the next day's average temperature drops below 2 degree Celsius
@app.route("/alerts", methods=["GET"])
def GET_alerts():
    alerts = alerts_getter()
    return alerts, 200
