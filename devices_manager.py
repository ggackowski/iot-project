import db.db as db_manager
import csv
import json
from datetime import datetime
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

endpoint = "a196zks8gm1dr-ats.iot.us-east-1.amazonaws.com"
shadows_dictionary = {}
private_key = ""
certificate = ""


def get_data_from_csv(loinc):
    csv_file = csv.reader(open("Loinc.csv", "r"), delimiter=",")
    for row in csv_file:
        if row[0] == loinc:
            return row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[26]


def measurement_callback(payload, response_status, token):
    if response_status == "accepted":
        print("Measurement accepted")


def on_add_measurement(payload, response_status, token):
    json_data = json.loads(payload)
    device_name = json_data['state']['desired']['welcome']
    patient_id = json_data['state']['desired']['patient_id']
    if patient_id == -1:
        return
    value = json_data['state']['desired']['indication']
    uuid = db_manager.get_device_from_name(device_name)[3]
    db_manager.add_measurement(value, uuid, patient_id, datetime.now(), )
    shadows_dictionary[device_name].shadowUpdate(json.dumps({'state': {'reported': {'indication': value}}}),
                                                 measurement_callback, 5)


def disconnected_callback(payload, response_status, token):
    if response_status == 'accepted':
        print("Device disconnected")


def on_disconnect(payload, response_status, token):
    json_data = json.loads(payload)
    prev_state = json_data['state']['reported']['status']
    name = json_data['state']['reported']['welcome']
    if prev_state == 'paired':
        patient_id = json_data['state']['reported']['patient_id']
        doctor_id = json_data['state']['reported']['doctor_id']
        uuid = db_manager.get_device_from_name(name)[3]
        db_manager.add_end_date_to_history(uuid, patient_id, doctor_id, datetime.now())
    print("Device " + name + " is unavailable")
    shadows_dictionary[name].shadowUpdate(json.dumps({'state':
                                                    {'desired': {'doctor_id': -1, 'patient_id': -1, 'indication': 0},
                                                      'reported': {'status': 'disconnected', 'doctor_id': -1,
                                                                             'patient_id': -1, 'indication': 0}}}),
                                          disconnected_callback, 5)


def delta_callback(payload, response_status, token):
    json_data = json.loads(payload)
    name = str(response_status).split('/')[1]
    if 'indication' in json_data['state']:
        shadows_dictionary[name].shadowGet(on_add_measurement, 5)
    if 'status' in json_data['state'] and (json_data['state']['status'] == 'disconnected'):
        shadows_dictionary[name].shadowGet(on_disconnect, 5)


def check_if_connected(payload, response_status, token):
    json_data = json.loads(payload)
    name = json_data['state']['reported']['welcome']
    if response_status == "accepted":
        shadows_dictionary[name].shadowRegisterDeltaCallback(delta_callback)
        print("Device " + name + " registered in manager")


def set_shadow_connection(device_name):
    global private_key, certificate
    json_data = json.load(open("device_certificates.json"))
    for record in json_data:
        if record['name'] == device_name:
            private_key = record['private_key']
            certificate = record['certificate']
            shadowClient = AWSIoTMQTTShadowClient(device_name + "devices_manager")
            shadowClient.configureEndpoint(endpoint, 8883)
            shadowClient.configureCredentials("../iot-project/certificates/Amazon_Root_CA_1.pem", private_key,
                                              certificate)
            shadowClient.configureConnectDisconnectTimeout(10)
            shadowClient.configureMQTTOperationTimeout(5)
            shadowClient.connect()
            deviceShadow = shadowClient.createShadowHandlerWithName(device_name, True)
            shadows_dictionary[device_name] = deviceShadow
            deviceShadow.shadowGet(check_if_connected, 5)


def run_mqtt():
    devices = db_manager.get_all_devices()
    if not devices:
        print("No devices in system")
        return
    for device in devices:
        device_name = device[1]
        set_shadow_connection(device_name)
        loinc_data = db_manager.get_loinc_data(device[2])
        if loinc_data is None:
            data = get_data_from_csv(device[2])
            db_manager.add_loinc_data(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7])


def add_new_device():
    print("Device name: ")
    name = input(">>")
    print("Device LOINC number:")
    loinc = input(">>")
    print("Device UUID:")
    uuid = input(">>")
    print("Device unit:")
    unit = input(">>")
    print("Minimum indication: ")
    minimum = input(">>")
    print("Maximum indication: ")
    maximum = input(">>")
    db_manager.add_device(name, loinc, uuid, unit, minimum, maximum)
    print("Device added to database")


def main():
    print("Welcome to device manager!")
    print("To add a new device press N")
    run_mqtt()
    while True:
        choice = input(">>")
        if choice == "N" or choice == "n":
            add_new_device()
        elif choice == '':
            return
        else:
            print("To add a new device press N")


if __name__ == "__main__":
    main()
