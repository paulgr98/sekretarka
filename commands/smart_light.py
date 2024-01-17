import discord
import components.smart_light as sl


def switch_main_lights() -> None:
    devs = sl.get_devices()
    podstawowe_1 = devs[3]
    podstawowe_2 = devs[2]

    sl.switch_state(podstawowe_1)
    sl.switch_state(podstawowe_2)


def switch_additional_lights() -> None:
    devs = sl.get_devices()
    dodatkowe_1 = devs[0]
    dodatkowe_2 = devs[1]

    sl.switch_state(dodatkowe_1)
    sl.switch_state(dodatkowe_2)


def get_status() -> str:
    devs = sl.get_devices()
    podstawowe_1 = devs[3]
    podstawowe_2 = devs[2]
    dodatkowe_1 = devs[0]
    dodatkowe_2 = devs[1]

    status = {
        "podstawowe_1": podstawowe_1.status(),
        "podstawowe_2": podstawowe_2.status(),
        "dodatkowe_1": dodatkowe_1.status(),
        "dodatkowe_2": dodatkowe_2.status()
    }

    return str(f'Podstawowe 1: {"ON" if bool(status["podstawowe_1"]["dps"]["20"]) else "OFF"}\n'
               f'Podstawowe 2: {"ON" if bool(status["podstawowe_2"]["dps"]["20"]) else "OFF"}\n'
               f'Dodatkowe 1: {"ON" if bool(status["dodatkowe_1"]["dps"]["20"]) else "OFF"}\n'
               f'Dodatkowe 2: {"ON" if bool(status["dodatkowe_2"]["dps"]["20"]) else "OFF"}')
