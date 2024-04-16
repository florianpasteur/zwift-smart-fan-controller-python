from openant.easy.node import Node
from openant.devices import ANTPLUS_NETWORK_KEY
from openant.devices.power_meter import PowerMeter, PowerData
from openant.devices.heart_rate import HeartRate, HeartRateData

import requests
import time
import json

last_change_time = 0
current_speed = 0


def main():
    node = Node()
    node.set_network_key(0x00, ANTPLUS_NETWORK_KEY)
    devices = []
    devices.append(PowerMeter(node))
    devices.append(HeartRate(node))
    fan_level(0)
    with open('power_meter_ranges.json', 'r') as file:
        power_meter_ranges = json.load(file)
        print(f"Configuration {power_meter_ranges['low']}")

    def on_found(device):
        print(f"Device {device} found and receiving")

    def on_device_data(page: int, page_name: str, data):
        if isinstance(data, PowerData):
            print(f"⚡️ {data.instantaneous_power} {data.average_power}")
            with open('power_meter_ranges.json', 'r') as file:
                power_meter_ranges = json.load(file)
                if data.average_power == 0:
                    fan_level(0)
                if data.average_power > 50:
                    fan_level(1)
                if data.average_power > 210:
                    fan_level(2)
                if data.average_power > 280:
                    fan_level(3)

        if isinstance(data, HeartRateData):
            print(f"❤️ {data.heart_rate}")

    for d in devices:
        d.on_found = lambda: on_found(d)
        d.on_device_data = on_device_data

    try:
        print(f"Starting {devices}, press Ctrl-C to finish")
        node.start()
    except KeyboardInterrupt:
        print("Closing ANT+ device...")
    finally:
        for d in devices:
            d.close_channel()
        node.stop()


def fan_level(speed):
    global last_change_time, current_speed
    current_time = time.time()

    if speed == current_speed:
        return

    # Check if the requested speed is lower than the current speed
    if speed < current_speed:
        # Check if 30 seconds have passed since the last speed change
        if current_time - last_change_time < 30:
            # Do not change the speed if less than 30 seconds have passed
            return

    requests.get('http://192.168.1.41/cm', params={'cmnd': 'Power0 Off'})
    if current_speed > 0:
        print(f"🪭 {current_speed}")
        requests.get('http://192.168.1.41/cm', params={'cmnd': 'Power{0}  On'.format(current_speed)})

    current_speed = speed
    last_change_time = current_time


if __name__ == "__main__":
    main()
