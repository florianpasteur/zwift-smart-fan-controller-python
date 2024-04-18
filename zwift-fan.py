from openant.easy.node import Node
from openant.devices import ANTPLUS_NETWORK_KEY
from openant.devices.power_meter import PowerMeter, PowerData
from openant.devices.heart_rate import HeartRate, HeartRateData

import requests
import time
import json

class BufferCount:
    def __init__(self, buffer_size: int = 3):
        self.values = []
        self.buffer_size = buffer_size

    def next(self, value):
        if len(self.values) == self.buffer_size:
            self.values.pop(0)
        self.values.append(value)

    def get_average(self):
        if not self.values:
            return 0
        return sum(self.values) / len(self.values)



with open('config.json', 'r') as f:
    config = json.load(f)

SLACK_WEBHOOK_URL = config["SLACK_WEBHOOK_URL"]

HR = BufferCount(5)
POWER = BufferCount(5)
FAN_SPEED = 0

def main():
    node = Node()
    node.set_network_key(0x00, ANTPLUS_NETWORK_KEY)
    devices = [PowerMeter(node), HeartRate(node)]
    fan_level(0)
    with open('power_meter_ranges.json', 'r') as file:
        power_meter_ranges = json.load(file)
        print(f"Configuration {power_meter_ranges['low']}")

    def on_found(device):
        print(f"Device {device} found and receiving")

    def on_device_data(page: int, page_name: str, data):
        if isinstance(data, PowerData):
            POWER.next(data.instantaneous_power)
        if isinstance(data, HeartRateData):
            HR.next(data.heart_rate)
        print(f"⚡️{POWER.get_average()} ❤️{HR.get_average()} 🪭{FAN_SPEED}")

    for d in devices:
        d.on_found = lambda: on_found(d)
        d.on_device_data = on_device_data

    try:
        print(f"Starting {devices}, press Ctrl-C to finish")
        log_to_slack("Fan has booted")
        node.start()
    except KeyboardInterrupt:
        print("Closing ANT+ device...")
    finally:
        for d in devices:
            d.close_channel()
        node.stop()


def fan_level(speed):
    global FAN_SPEED
    # requests.get('http://192.168.1.41/cm', params={'cmnd': 'Power0 Off'})
    # if current_speed > 0:
    #     requests.get('http://192.168.1.41/cm', params={'cmnd': 'Power{0}  On'.format(current_speed)})

    FAN_SPEED = speed

def log_to_slack(message):
    payload = {
        "text": message,
        "username": "Fan Speed Logger",
        "icon_emoji": ":gear:",  # You can customize the emoji
    }

    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            print(f"Failed to send message to Slack: {response.content}")
    except Exception as e:
        print(f"Error sending message to Slack: {e}")


if __name__ == "__main__":
    main()


