import mqtt_driver
import time
import random
import sys
sys.path.insert(0, '../')
from device import Device

DEVICE_PARAMETERS = {
    "loinc_num": "29463-7",
    "loinc_long_common_name": "Body weight",
    "hash": "nfjdhfkjd",
    "minimal_measurement": 1,
    "maximal_measurement": 240,
    "unit": 0
}

if __name__ == "__main__":
    device = Device("../../../config/body_weight_scales_kg_d2f0df80/0ee175d973-private.pem.key",
                "../../../config/body_weight_scales_kg_d2f0df80/0ee175d973-certificate.pem.crt",
                "body_weight_scales_kg_d2f0df80", "a196zks8gm1dr-ats.iot.us-east-1.amazonaws.com", "body_weight_scales_kg_d2f0df80", DEVICE_PARAMETERS)



