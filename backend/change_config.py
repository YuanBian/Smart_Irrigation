import argparse
import json

config_f = open("/Users/yuanbian/Desktop/smart_irrigation/backend/config.json","r")
configs = json.load(config_f)
config_f.close()

parser = argparse.ArgumentParser(description='Parameters for irrigation system')
parser.add_argument('--valveTime', dest='valveTime', type=int, action='store',
                    default=configs["valveTime"])

parser.add_argument('--photoTimeInterval', dest='photoTimeInterval',type=int, action='store',
                    default=configs["photoTimeInterval"])

parser.add_argument('--moistureSensorCheckTime', dest='moistureSensorCheckTime',type=int, action='store',
                    default=configs["moistureSensorCheckTime"])

parser.add_argument('--frostWarningThreshold', dest='frostWarningThreshold', type=int, action='store',
                    default=configs["frostWarningThreshold"])

args = parser.parse_args()
valveTime = args.valveTime
photoTimeInterval = args.photoTimeInterval
moistureSensorCheckTime = args.moistureSensorCheckTime
frostWarningThreshold = args.frostWarningThreshold
emails = configs["emails"]

new_configs = {
  "valveTime": valveTime,
  "photoTimeInterval": photoTimeInterval,
  "moistureSensorCheckTime": moistureSensorCheckTime,
  "emails":emails,
  "frostWarningThreshold": frostWarningThreshold
}

new_configs_str = json.dumps(new_configs)
new_config_f = open("/Users/yuanbian/Desktop/smart_irrigation/backend/config.json","w")
new_config_f.write(new_configs_str)
new_config_f.close()

print("current configs: "+new_configs_str)