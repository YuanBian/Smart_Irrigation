from flask import Flask, render_template, request, jsonify
import os
import requests
from datetime import datetime, timedelta, time
import re
from dotenv import load_dotenv

load_dotenv()
COURSES_MICROSERVICE_URL = os.getenv("COURSES_MICROSERVICE_URL")

app = Flask(__name__)


def parse_course(course_str):
    str_split = re.findall("\d+|\D+", course_str)
    subject, number = "x", "x"
    if len(str_split) == 2:
        subject = str_split[0].strip().upper()
        number = str_split[1].strip()
    return (subject, number)


def time_convert(am_pm):  # convert am pm time format to 24 hours format
    in_time = datetime.strptime(am_pm, "%I:%M %p")
    out_time = datetime.strftime(in_time, "%H:%M:%S")
    return out_time


def get_nearest_class_time(course_json):
    # turn MTWRF to 12345
    weekdays_to_num = {"M": 1, "T": 2, "W": 3, "R": 4, "F": 5}
    course_weekdays = [weekdays_to_num[x] for x in course_json["Days of Week"]]
    course_weekdays.sort()
    today_weekday = datetime.today().isoweekday()
    start_time = time_convert(course_json["Start Time"])
    print(start_time)
    print(type(start_time))
    nearest_date = ""
    cur_time = datetime.now().time()
    if today_weekday > max(course_weekdays):  # the next course is next week
        nearest_date = datetime.now().date() + timedelta(
            days=(7 - today_weekday) + min(course_weekdays)
        )
    elif today_weekday in course_weekdays:  # the course is today, or it already passed
        if (
            datetime.strptime(start_time, "%H:%M:%S")
            - datetime.now().replace(year=1900, month=1, day=1)
        ).days >= 0:
            nearest_date = str(datetime.now().date())  # today
        else:
            if today_weekday >= max(course_weekdays):
                nearest_date = datetime.now().date() + timedelta(
                    days=(7 - today_weekday) + min(course_weekdays)
                )
            else:
                diff_days = [x for x in course_weekdays if x > today_weekday][
                    0
                ] - today_weekday
                nearest_date = datetime.now().date() + timedelta(days=diff_days)
    else:
        diff_days = [x for x in course_weekdays if x > today_weekday][0] - today_weekday
        nearest_date = datetime.now().date() + timedelta(days=diff_days)
    nearest_class_time = f"{nearest_date} {start_time}"
    return nearest_class_time


def get_forecast(class_time):
    class_time = class_time.replace(" ", "T")[:-6]
    weather_data = requests.get(
        "https://api.weather.gov/points/40.1125,-88.2284"
    ).json()
    hourly_api = weather_data["properties"]["forecastHourly"]
    hourly_data = requests.get(hourly_api).json()["properties"]["periods"]
    shortForecast, temperature, forecastTime = "", "", ""
    for data in hourly_data:
        cur_time = data["startTime"][:-6]
        if class_time in cur_time:
            shortForecast = data["shortForecast"]
            temperature = data["temperature"]
            forecastTime = data["startTime"].replace("T", " ")[:-6]
            break
    return {
        "shortForecast": shortForecast,
        "temperature": temperature,
        "forecastTime": forecastTime,
    }


def check_time_range(time):
    time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    return (time - datetime.now()).total_seconds() / 3600.0 <= 156.0


# Route for "/" (frontend):
@app.route("/")
def index():
    return render_template("index.html")


# Route for "/weather" (middleware):
@app.route("/weather", methods=["POST"])
def POST_weather():
    course = request.form["course"]
    # is_course = re.search(r"[a-zA-Z]{2,5}\s*\d{3}", course) != None
    subject, number = parse_course(course)
    course_json = requests.get(f"{COURSES_MICROSERVICE_URL}/{subject}/{number}/").json()
    is_course = "error" not in course_json
    temperature, shortForecast, forecastTime = "", "", ""
    if is_course:
        subject, number = parse_course(course)
        course_json = requests.get(
            f"{COURSES_MICROSERVICE_URL}/{subject}/{number}/"
        ).json()

        nearest_class_time = get_nearest_class_time(course_json)
        forecast = get_forecast(nearest_class_time)
        temperature, shortForecast, forecastTime = (
            forecast["temperature"],
            forecast["shortForecast"],
            forecast["forecastTime"],
        )
        print("HERE")
        # check if the class is more than 144 hours away
        forecast_avaible = check_time_range(nearest_class_time)
        if not forecast_avaible:
            temperature, shortForecast = "forecast unavailable", "forecast unavailable"
        ret_json = (
            jsonify(
                {
                    "course": f"{subject} {number}",
                    "nextCourseMeeting": nearest_class_time,
                    "forecastTime": forecastTime,
                    "temperature": temperature,
                    "shortForecast": shortForecast,
                }
            ),
            200,
        )
        return ret_json

    else:
        return jsonify({"error": "Some error occurred."}), 400
