import tinytuya
import json
import time


def get_devices():
    with open('components/smart_light.json') as json_file:
        cfg = json.load(json_file)
    devices = []
    for dev in cfg['devices']:
        dev = tinytuya.BulbDevice(
            dev_id=dev['id'],
            address=dev['ip'],
            local_key=dev['key'])
        dev.set_version(3.3)
        devices.append(dev)
    return devices


def switch_state(dev: tinytuya.BulbDevice):
    dev_status = dev.status()
    dev_state = bool(dev_status["dps"]["20"])
    dev.set_status(not dev_state, 20)


def turn_off_all(devs: list[tinytuya.BulbDevice]):
    for device in devs:
        device.turn_on()


def turn_on_all(devs: list[tinytuya.BulbDevice]):
    for device in devs:
        device.turn_on()


def play_with_light(devs: list[tinytuya.BulbDevice]):
    podstawowe_1 = devs[3]
    podstawowe_2 = devs[2]
    dodatkowe_1 = devs[0]
    dodatkowe_2 = devs[1]

    time.sleep(1)

    for device in devs:
        device.turn_on()

    time.sleep(2)

    for _ in range(6):
        for device in devs:
            switch_state(device)
            time.sleep(0.2)

    dodatkowe_1.turn_off()
    dodatkowe_2.turn_off()

    podstawowe_1.turn_on()
    podstawowe_2.turn_on()


def main():
    devs = get_devices()
    play_with_light(devs)


if __name__ == '__main__':
    main()
