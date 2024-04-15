"""
Example of using mulitple devices: a PowerMeter and FitnessEquipment.

Also demos Workout feature of FitnessEquipment, where the device has a thread and sends info to the master.

Refer to subparsers/influx for another example of creating multiple devices at runtime
"""
from openant.easy.node import Node
from openant.devices import ANTPLUS_NETWORK_KEY
from openant.devices.power_meter import PowerMeter, PowerData

def main():
    import logging

    # logging.basicConfig(level=logging.INFO)
    node = Node()
    node.set_network_key(0x00, ANTPLUS_NETWORK_KEY)
    devices = []


    devices.append(PowerMeter(node))

    def on_found(device):
        print(f"Device {device} found and receiving")

    def on_device_data(page: int, page_name: str, data):
        if isinstance(data, PowerData):
            print(f"PowerMeter {data.instantaneous_power}")

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


if __name__ == "__main__":
    main()
