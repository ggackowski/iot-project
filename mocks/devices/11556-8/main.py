import mqtt_driver
import time
import random
import sys
sys.path.insert(0, '../')
from device import Device

DEVICE_PARAMETERS = {
    "loinc_num": "11556-8",
    "loinc_long_common_name": "Oxygen [Partial pressure] in Blood",
    "hash": "adjfkeor",
    "minimal_measurement": 20,
    "maximal_measurement": 140,
    "unit": 0
}

if __name__ == "__main__":
    device = Device("../../../config/Oxygen_fd70ed88/0ee175d973-private.pem.key",
                "../../../config/Oxygen_fd70ed88/0ee175d973-certificate.pem.crt",
                "Oxygen_fd70ed88", "a196zks8gm1dr-ats.iot.us-east-1.amazonaws.com", "Oxygen_fd70ed88", DEVICE_PARAMETERS)


