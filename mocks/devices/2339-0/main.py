import mqtt_driver
import time
import random
import sys
sys.path.insert(0, '../')
from device import Device

DEVICE_PARAMETERS = {
    "loinc_num": "2339-0",
    "loinc_long_common_name": "Glucose [Mass/volume] in Blood",
    "hash": "dnbjgktr",
    "minimal_measurement": 80,
    "maximal_measurement": 150,
    "unit": 0
}

# hospital_hash = "xxxxxx"

# def set_hospital_hash(hash):
#     global hospital_hash
#     hospital_hash = hash

# def generate_measurement_from_range(min, max):
#     return random.randint(start, stop)

# def generate_measurement():
#     return str(random.randint(DEVICE_PARAMETERS['minimal_measurement'], DEVICE_PARAMETERS['maximal_measurement']))

# def add_to_database():
#     mqtt_driver.send_device_data_to_manager(DEVICE_PARAMETERS['loinc_num'], DEVICE_PARAMETERS['loinc_long_common_name'])

# def pair():
#     mqtt_driver.set_mqtt_subscriptions_to_state__pair()
#     mqtt_driver.send_pair_request()

# def measure():
#     mqtt_driver.send_measurement(generate_measurement(), DEVICE_PARAMETERS['unit'])

# def unpair():
#     mqtt_driver.set_mqtt_subscriptions_to_state__unpair()
#     mqtt_driver.send_unpair_request()

# def set_parameters():
#     mqtt_driver.set_device_hash(DEVICE_PARAMETERS["hash"])
#     mqtt_driver.set_device_type(DEVICE_PARAMETERS["loinc_num"])
#     mqtt_driver.set_hospital_hash(hospital_hash)

# def execute_user_input():
#     text = input(">> ")
#     if text == "pair":
#         pair()
#     if text == "measure":
#         measure()
#     if text == "unpair":
#         unpair()

if __name__ == "__main__":
    device = Device("../../../config/glucometer_2339_0/0ee175d973-private.pem.key",
                "../../../config/glucometer_2339_0/0ee175d973-certificate.pem.crt",
                "glucometer_17432f61", "a196zks8gm1dr-ats.iot.us-east-1.amazonaws.com", "glucometer_17432f61", DEVICE_PARAMETERS)
    # set_hospital_hash("clinic1234")
    # set_parameters()
    # mqtt_driver.run()
    # time.sleep(1)
    # add_to_database()
    # while True:
    #     execute_user_input()


