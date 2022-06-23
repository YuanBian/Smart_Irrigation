# Smart Irrigation System

For the final project in the IoT class, I designed a smart irrigation system for my backyard. The system will detect the current weather from open weather APIs, and moisture level from moisture sensors plugged into the ground, and automatically water the guarden through soaker hoses if conditions are met (i.e. not raining today && ground is not wet).

The backend and frontend of the system is created by Python Flask App. The backend interacts with the hardwares of the Raspberry Pi, triggered by API calls from the frontend. The frontend hosts interface that allows user to interact with the backend's hardware, and to manually configure settings for the backend (i.e. how long the irrigation lasts, what time to start irrigation, etc).

The frontend and backend are both hosted on Raspberry Pi, but the frontend will eventually be moved to another computer.

## How to use the code

1. After cloning the code to your local machine, and plugging in the moisture sensors and valves to your Raspberry Pi, change the configs of SENSOR_INPUTS and VALVE_OUTPUTS in smart_irrigation/backend/config.json.

2. Set up python venv:

   python3 -m venv venv

   source ./venv/bin

3. install required packages inside the venv:

   pip install -r requirements

4. run:

   cd smart_irrigation/backend

   flask run &

   cd ../

   flask run &
