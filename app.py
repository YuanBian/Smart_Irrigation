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
def alerts_getter():
    general_alerts = ""
    frost_warning = ""
    default_no_warning = general_alerts+frost_warning
    weather_data = requests.get(WEATHER_API).json()
    try: 
        general_alerts = json.dumps(weather_data["alerts"])
    except:
        pass
    min_temp = kelvinToCelsius(weather_data["daily"][1]["temp"]["min"]) # check temp for the next week
    if min_temp<=2:
        frost_warning = "There is frost tomorrow! "
    msg_text = general_alerts+frost_warning
    return msg_text

def send_email():
    print("hello")
    alerts = alerts_getter()
    if alerts !="":
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.login('yuanbian95@gmail.com', APP_PASSWORD)
        msg = MIMEMultipart()
        msg['Subject'] = "Weather Warning"
        msg.attach(MIMEText(alerts))
        to = ["mklimuszka@gmail.com"]
        smtp.sendmail(from_addr="yuanbian95@gmail.com",
                    to_addrs=to, msg=msg.as_string())
        smtp.quit()

sched = BackgroundScheduler()
# sched.add_job(send_email,'cron',hour=2 , minute=31)
sched.add_job(send_email,'cron',hour=8, minute=0, timezone="America/Chicago")
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
    res = requests.post('http://127.0.0.1:5000/configs', data=json.dumps(updated_configs))
    return "Status code: "+str(res.status_code)

# water now
@app.route("/water_now", methods=["GET"])
def GET_waterNow():
    res = requests.get("http://192.168.1.38:5000/water")
    return "Status code: "+str(res.status_code)

@app.route("/stop_water", methods=["GET"])
def GET_stop_water():
    res = requests.get("http://192.168.1.38:5000/stop_water")
    return "Status code: "+str(res.status_code)
  
# use sensor now
@app.route("/get_sensor_now", methods=["GET"])
def GET_sensor():
    res = requests.get("http://127.0.0.1:5000/sensor").json()
    return "Sensor data: "+str(res)

# get pi temperature
@app.route("/pi_temperature", methods=["GET"])
def GET_pi_temperature():
    r = requests.get("http://127.0.0.1:5000/pi_temperature").json()
    return r["pi_temperature"]

# get pi temperature
# @app.route("/get_chart", methods=["GET"])
# def GET_chart():
#     r = requests.get("http://127.0.0.1:5000/chart").json()
#     return 

# @app.route("/get_camera_now", methods=["GET"])
# def GET_camera():
#     now = datetime.now()
#     dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
#     img_path = "/home/pi/garden_services/smart_irrigation/photos/garden "+dt_string+".jpg"
#     r = requests.get("http://127.0.0.1:5000/pi_temperature")
#     print(r)
#     print(request.args)
#     return "img"

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

