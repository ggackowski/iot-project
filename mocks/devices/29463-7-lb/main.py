import mqtt_driver
import time
import random
import sys
sys.path.insert(0, '../')
from device import Device

DEVICE_PARAMETERS = {
    "loinc_num": "29463-7",
    "loinc_long_common_name": "Body weight",
    "hash": "8e2eeb34-6981-11eb-9439-0242ac130002",
    "minimal_measurement": 2,
    "maximal_measurement": 440,
    "unit": "lb"
}

if __name__ == "__main__":
    device = Device("../../../config/body_weight_scales_lb_8e2eeb34/0ee175d973-private.pem.key",
                "../../../config/body_weight_scales_lb_8e2eeb34/0ee175d973-certificate.pem.crt",
                "body_weight_scales_lb_8e2eeb34", "a196zks8gm1dr-ats.iot.us-east-1.amazonaws.com", "body_weight_scales_lb_8e2eeb34", DEVICE_PARAMETERS)

