import mqtt_driver
import time
import random
import sys
sys.path.insert(0, '../')
from device import Device

DEVICE_PARAMETERS = {
    "loinc_num": "15074-8",
    "loinc_long_common_name": "Glucose [Moles/volume] in Blood",
    "hash": "kmvkjfkf",
    "minimal_measurement": 80,
    "maximal_measurement": 100,
    "unit": 0
}

if __name__ == "__main__":
    device = Device("../../../config/glucometer_4fe3ba2a/0ee175d973-private.pem.key",
                "../../../config/glucometer_4fe3ba2a/0ee175d973-certificate.pem.crt",
                "glucometer_4fe3ba2a", "a196zks8gm1dr-ats.iot.us-east-1.amazonaws.com", "glucometer_4fe3ba2a", DEVICE_PARAMETERS)


