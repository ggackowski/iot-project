import mqtt_driver
import time

DEVICE_PARAMETERS = {
    "loinc_num": "1",
    "loinc_long_common_name": "Oxygen [Partial pressure] in Blood",
    "hash": "a"
}

hospital_hash = "xxxxxx"

def set_hospital_hash(hash):
    global hospital_hash
    hospital_hash = hash

def add_to_database():
    mqtt_driver.set_mqtt_subscriptions_to_state__add_to_database()
    mqtt_driver.send_device_data_to_manager()

def pair():
    mqtt_driver.set_mqtt_subscriptions_to_state__pair()
    mqtt_driver.send_pair_request()

def measure():
    mqtt_driver.send_measurement("measurement")

def unpair():
    mqtt_driver.set_mqtt_subscriptions_to_state__unpair()
    mqtt_driver.send_unpair_request()

def set_parameters():
    mqtt_driver.set_device_hash(DEVICE_PARAMETERS["hash"])
    mqtt_driver.set_device_type(DEVICE_PARAMETERS["loinc_num"])
    mqtt_driver.set_hospital_hash(hospital_hash)

def execute_user_input():
    text = input(">> ")
    if text == "add_to_database":
        add_to_database()
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
    while True:
        execute_user_input()


