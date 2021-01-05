import mqtt_driver
import time
import random

DEVICE_PARAMETERS = {
    "loinc_num": "29463-7",
    "loinc_long_common_name": "Body weight",
    "hash": "nfjdhfkjd",
    "minimal_measurement": 1,
    "maximal_measurement": 240
}

hospital_hash = "xxxxxx"

def set_hospital_hash(hash):
    global hospital_hash
    hospital_hash = hash

def generate_measurement_from_range(min, max):
    return random.randint(start, stop)

def generate_measurement():
    return str(random.randint(DEVICE_PARAMETERS['minimal_measurement'], DEVICE_PARAMETERS['maximal_measurement']))

def add_to_database():
    mqtt_driver.send_device_data_to_manager(DEVICE_PARAMETERS['loinc_num'], DEVICE_PARAMETERS['loinc_long_common_name'])
    mqtt_driver.set_device_id(DEVICE_PARAMETERS['hash'])

def pair():
    mqtt_driver.set_mqtt_subscriptions_to_state__pair()
    mqtt_driver.send_pair_request()

def measure():
    mqtt_driver.send_measurement(generate_measurement())

def unpair():
    mqtt_driver.set_mqtt_subscriptions_to_state__unpair()
    mqtt_driver.send_unpair_request()

def set_parameters():
    mqtt_driver.set_device_hash(DEVICE_PARAMETERS["hash"])
    mqtt_driver.set_device_type(DEVICE_PARAMETERS["loinc_num"])
    mqtt_driver.set_hospital_hash(hospital_hash)

def execute_user_input():
    text = input(">> ")
    if text == "pair":
        pair()
    if text == "measure":
        measure()
    if text == "unpair":
        unpair()

if __name__ == "__main__":
    set_hospital_hash("clinic1234")
    set_parameters()
    mqtt_driver.run()
    time.sleep(1)
    add_to_database()
    while True:
        execute_user_input()


