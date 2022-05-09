from flask import Flask, render_template, request, jsonify
import os
import requests
from datetime import datetime, timedelta, time
import re
from dotenv import load_dotenv
import datetime

app = Flask(__name__)

@app.route("/weather", methods=["GET"])
def GET_weather():
    return 0

@app.route("/alerts", methods=["GET"])
def GET_alerts():
    return 0

@app.route("/analysis/<mode>", methods=["GET"])
def GET_analysis(mode):
    return 0