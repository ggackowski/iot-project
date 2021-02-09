import threading
import random
import string
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import json
import db.db as db_manager
from datetime import datetime

doctor_id = ""
patient_id = ""
endpoint = "a196zks8gm1dr-ats.iot.us-east-1.amazonaws.com"
doctor_hash = random.choice(string.ascii_letters) + str(random.randrange(0, 900))
shadows_dictionary = {}
paired_shadows_dictionary = {}
shadow_clients = {}
private_key = ""
certificate = ""


def set_paired_connection(device_name):
    global private_key, certificate
    json_data = json.load(open("device_certificates.json"))
    for record in json_data:
        if record['name'] == device_name:
            private_key = record['private_key']
            certificate = record['certificate']
            shadowClient = AWSIoTMQTTShadowClient(device_name + doctor_hash)
            shadowClient.configureEndpoint(endpoint, 8883)
            shadowClient.configureCredentials("../iot-project/certificates/Amazon_Root_CA_1.pem", private_key,
                                              certificate)
            shadowClient.configureConnectDisconnectTimeout(10)
            shadowClient.configureMQTTOperationTimeout(5)
            shadowClient.connect()
            shadow_clients[device_name] = shadowClient
            deviceShadow = shadowClient.createShadowHandlerWithName(device_name, True)
            paired_shadows_dictionary[device_name] = deviceShadow
            paired_shadows_dictionary[device_name].shadowRegisterDeltaCallback(delta_callback)
            print("Successfully paired with device " + device_name)


def set_paired_devices():
    results = db_manager.get_devices_paired_with_doctor(doctor_id)
    if not results:
        return
    for result in results:
        set_paired_connection(result[0])


def get_doctor_id():
    global doctor_id
    print("Welcome to Smart Medical Devices Management System!")
    print("Please enter your name:")
    doctor_name = input(">>")
    print("Please enter your surname:")
    doctor_surname = input(">>")
    doctor = db_manager.get_doctor_id(doctor_name, doctor_surname)
    if doctor is None:
        db_manager.add_doctor(doctor_name, doctor_surname)
        doctor_id = db_manager.get_doctor_id(doctor_name, doctor_surname)[0]
    else:
        doctor_id = doctor[0]
    set_paired_devices()


def set_patient_id():
    global patient_id
    print("Please enter patient name:")
    name = input(">>")
    print("Please enter patient surname:")
    surname = input(">>")
    patient = db_manager.get_patient_id(name, surname)
    if patient is None:
        db_manager.add_patient(name, surname)
        patient_id = db_manager.get_patient_id(name, surname)[0]
    else:
        patient_id = patient[0]
    print("Current patient id: " + str(patient_id))


def delta_callback(payload, response_status, token):
    json_data = json.loads(payload)
    name = str(response_status).split('/')[1]
    if 'status' in json_data['state'] and (json_data['state']['status'] == 'disconnected'):
        print("Device " + name + " is unavailable")
        if name in shadows_dictionary:
            shadows_dictionary[name].shadowUnregisterDeltaCallback()
            shadows_dictionary.pop(name)
        elif name in paired_shadows_dictionary:
            paired_shadows_dictionary[name].shadowUnregisterDeltaCallback()
            paired_shadows_dictionary.pop(name)
        shadow_clients[name].disconnect()
        shadow_clients.pop(name)
    if 'status' in json_data['state'] and json_data['state']['status'] == 'paired':
        if 'doctor_id' in json_data['state'] and json_data['state']['doctor_id'] == doctor_id:
            paired_shadows_dictionary[name] = shadows_dictionary[name]
            shadows_dictionary.pop(name)
        else:
            print("Device " + name + " is unavailable")
            shadows_dictionary.pop(name)
        shadow_clients[name].disconnect()
        shadow_clients.pop(name)


def check_if_connected(payload, response_status, token):
    json_data = json.loads(payload)
    name = json_data['state']['reported']['welcome']
    if json_data['state']['reported']['status'] == 'connected':
        shadows_dictionary[name].shadowRegisterDeltaCallback(delta_callback)
        print("Successfully connected to device " + name)
    else:
        print("Device " + name + " is currently unavailable")
        shadows_dictionary.pop(name)
        shadow_clients[name].disconnect()
        shadow_clients.pop(name)


def set_shadow_connection(device_name):
    global private_key, certificate
    json_data = json.load(open("device_certificates.json"))
    if device_name in shadows_dictionary or (device_name in paired_shadows_dictionary):
        return
    for record in json_data:
        if record['name'] == device_name:
            private_key = record['private_key']
            certificate = record['certificate']
            shadowClient = AWSIoTMQTTShadowClient(device_name + doctor_hash)
            shadowClient.configureEndpoint(endpoint, 8883)
            shadowClient.configureCredentials("../iot-project/certificates/Amazon_Root_CA_1.pem", private_key,
                                              certificate)
            shadowClient.configureConnectDisconnectTimeout(10)
            shadowClient.configureMQTTOperationTimeout(5)
            shadowClient.connect()
            shadow_clients[device_name] = shadowClient
            deviceShadow = shadowClient.createShadowHandlerWithName(device_name, True)
            shadows_dictionary[device_name] = deviceShadow
            deviceShadow.shadowGet(check_if_connected, 5)


def connect_new_device():
    results = db_manager.get_all_devices()
    available_devices = []
    if not results:
        print("No devices available")
        return
    for result in results:
        available_devices.append(result[1])
    print("Devices list:")
    i = 0
    for device in available_devices:
        print(str(i) + " - " + device)
        i += 1
    print("Please select number for device")
    number = int(input(">> "))
    if 0 <= number < i:
        device_name = results[number][1]
    else:
        print("Invalid device number")
        return
    set_shadow_connection(device_name)


def paired_callback(payload, response_status, token):
    if response_status == "accepted":
        print("Device paired")


def pair_with_patient():
    if patient_id == '':
        print("Set patient id first!")
        return
    results = shadows_dictionary.keys()
    if not results:
        print("No devices connected with doctor")
        return
    results_table = list(results)
    connected_devices = []
    i = 0
    for result in results_table:
        data = db_manager.get_device_data(result)
        connected_devices.append(str(i) + " - " + result + " ,LOINC: " + data[2] + " ,unit:" + data[4])
        i += 1
    print("Connected devices:")
    for device in connected_devices:
        print(device)
    print("Please select number for device")
    number = int(input(">> "))
    if 0 <= number < len(connected_devices):
        name = results_table[number]
    else:
        print("Invalid device number")
        return
    shadows_dictionary[name].shadowUpdate(json.dumps({"state": {"desired": {"status": "paired", "doctor_id": doctor_id,
                                                                            "patient_id": patient_id}}}),
                                          paired_callback, 5)
    device_uuid = db_manager.get_device_from_name(name)[3]
    db_manager.start_device_history(device_uuid, patient_id, doctor_id, datetime.now())


def disconnect_callback(payload, response_status, token):
    if response_status == "accepted":
        print("Device unpaired")


def unpair_device():
    if patient_id == '':
        print("Set patient id first!")
        return
    results = paired_shadows_dictionary.keys()
    if not results:
        print("No devices connected with doctor")
        return
    results_table = list(results)
    connected_devices = []
    i = 0
    for result in results_table:
        data = db_manager.get_device_data(result)
        connected_devices.append(str(i) + " - " + result + " ,LOINC: " + data[2] + " ,unit:" + data[4])
        i += 1
    print("Connected devices:")
    for device in connected_devices:
        print(device)
    print("Please select number for device")
    number = int(input(">> "))
    if 0 <= number < len(connected_devices):
        name = results_table[number]
    else:
        print("Invalid device number")
        return
    paired_shadows_dictionary[name].shadowUpdate(
        json.dumps({'state': {'desired': {'status': 'connected', 'doctor_id': -1,
                                          'patient_id': -1}}}),
        disconnect_callback, 5)
    device_uuid = db_manager.get_device_from_name(name)[3]
    db_manager.add_end_date_to_history(device_uuid, patient_id, doctor_id, datetime.now())
    shadows_dictionary[name] = paired_shadows_dictionary[name]
    paired_shadows_dictionary.pop(name)


def disconnect_from_all_devices():
    results = shadows_dictionary.keys()
    results_table = list(results)
    if results_table:
        for result in results_table:
            shadows_dictionary[result].shadowUpdate(
                json.dumps({'state': {'desired': {'status': 'connected', 'doctor_id': -1,
                                                  'patient_id': -1}}}),
                disconnect_callback, 5)


def get_patient_data():
    if patient_id == '':
        print("Set patient id first!")
        return
    results = db_manager.get_patient_measurements(patient_id)
    if not results:
        print("No data for patient")
        return
    for result in results:
        unit = result[6]
        print("Data for " + result[0] + " " + result[1] + ": " + str(result[2]) + " " + unit + " from " + result[3])
        print("Date and time of measurement: " + result[5].strftime("%d/%m/%Y %H:%M:%S"))


def get_device_description():
    results = db_manager.get_all_devices()
    devices = []
    i = 0
    if not results:
        print("No devices in database")
        return
    for result in results:
        devices.append(str(i) + " - " + result[1] + " ,LOINC: " + result[2] + " ,unit:" + result[4])
        i += 1
    print("Available devices:")
    for device in devices:
        print(device)
    print("Please select number for device")
    number = int(input(">> "))
    if 0 <= number < len(devices):
        device_loinc = results[number][2]
    else:
        print("Invalid device number")
        return
    data = db_manager.get_loinc_data(device_loinc)
    attributes = results[number]
    if not data:
        print("No data for selected device")
        return
    print("Device attributes for device " + attributes[1] + "\n UUID: " + attributes[3] + "\n Unit: " + attributes[4]
          + "\n Minimum indication: " + str(attributes[5]) + " Maximum indication: " + str(attributes[6]))
    print("Device parameters for LOINC " + data[6] + ": \n Component: " + data[7] + "\n Kind of property: " + data[4] +
          "\n Time aspect: " + data[1] + "\n System: " + data[2] + "\n Type of scale: " + data[
              3] + "\n Type of method: " +
          data[5])


def get_device_history():
    results = db_manager.get_all_devices()
    devices = []
    i = 0
    if not results:
        print("No devices in database")
        return
    for result in results:
        devices.append(str(i) + " - " + result[1] + " ,LOINC: " + result[2] + " ,unit:" + result[4])
        i += 1
    print("Available devices:")
    for device in devices:
        print(device)
    print("Please select number for device")
    number = int(input(">> "))
    if 0 <= number < len(devices):
        uuid = results[number][3]
    else:
        print("Invalid device number")
        return
    history = db_manager.get_device_history(uuid)
    if not history:
        print("No history for device")
        return
    for result in history:
        print("\n Patient id: " + str(result[2]) + ", Doctor id: " + str(result[3]) + " ,Start date: "
              + result[4].strftime("%d/%m/%Y %H:%M:%S") +
              " ,End date: " + result[5].strftime("%d/%m/%Y %H:%M:%S"))


def navigate():
    print("What do you want to do? (Enter the number for the selected action) \n 1 - set patient id "
          "\n 2 - connect new device \n 3 - pair device with patient \n 4 - unpair device \n"
          " 5 - get device history \n 6 - get current patient data \n 7 - get device description")
    choice = input(">>")
    if choice == "1":
        set_patient_id()
    elif choice == "2":
        connect_new_device()
    elif choice == "3":
        pair_with_patient()
    elif choice == "4":
        unpair_device()
    elif choice == "5":
        get_device_history()
    elif choice == "6":
        get_patient_data()
    elif choice == "7":
        get_device_description()
    elif choice == '':
        return
    else:
        print("Please enter number from 1 to 5")


def main():
    get_doctor_id()
    while True:
        navigate()


if __name__ == "__main__":
    main()
