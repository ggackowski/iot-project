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
doctor_hash = random.choice(string.ascii_letters) + random.randrange(0, 900)
shadows_dictionary = {}
private_key = ""
certificate = ""


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
    if 'status' in json_data['state'] and json_data['state']['status'] == 'disconnected':
        print("Device " + name + " is disconnected")
        shadows_dictionary.pop(name)


def check_if_connected(payload, response_status, token):
    json_data = json.loads(payload)
    name = json_data['state']['reported']['welcome']
    if json_data['state']['reported']['status'] == 'connected':
        shadows_dictionary[name].shadowRegisterDeltaCallback(delta_callback)
        print("Successfully connected to device " + name)
    else:
        print("Device " + name + " is currently unavailable")
        shadows_dictionary.pop(name)


def set_shadow_connection(device_name):
    global private_key, certificate
    json_data = json.load(open("device_certificates.json"))
    for record in json_data:
        if record['name'] == device_name:
            private_key = record['private_key']
            certificate = record['certificate']
        else:
            print("Did not find certificates for device")
    shadowClient = AWSIoTMQTTShadowClient(device_name + doctor_hash)
    shadowClient.configureEndpoint(endpoint, 8883)
    shadowClient.configureCredentials("../iot-project/certificates/Amazon_Root_CA_1.pem", private_key,
                                      certificate)
    shadowClient.configureConnectDisconnectTimeout(10)
    shadowClient.configureMQTTOperationTimeout(5)
    shadowClient.connect()
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
    results_table = []
    for result in results:
        results_table.append(result)
    connected_devices = []
    i = 0
    for result in results_table:
        data = db_manager.get_device_data(result)
        connected_devices.append(str(i) + " - " + result + " ,LOINC: " + data[1] + " ,unit:" + data[3])
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
    shadows_dictionary[name].shadowUpdate(json.dumps({'state': {'desired': {'status': 'paired', 'doctor_id': doctor_id,
                                                                            'patient_id': patient_id}}}),
                                          paired_callback, 5)


def disconnect_callback(payload, response_status, token):
    if response_status == "accepted":
        print("Device disconnected")


def disconnect_device():
    results = shadows_dictionary.keys()
    if not results:
        print("No devices connected with doctor")
        return
    results_table = []
    for result in results:
        results_table.append(result)
    connected_devices = []
    i = 0
    for result in results_table:
        data = db_manager.get_device_data(result)
        connected_devices.append(str(i) + " - " + result + " ,LOINC: " + data[1] + " ,unit:" + data[3])
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
    shadows_dictionary[name].shadowUpdate(json.dumps({'state': {'desired': {'status': 'connected', 'doctor_id': -1,
                                                                            'patient_id': -1}}}),
                                          disconnect_callback, 5)


def disconnect_from_all_devices():
    results = shadows_dictionary.keys()
    results_table = []
    for result in results:
        results_table.append(result)
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
        data = db_manager.get_loinc_data(result[4])
        unit = data[8].split(";")[result[6]]
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
        devices.append(str(i) + " - " + str(result[0]) + " " + result[1] + " " + result[2])
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
    if not data:
        print("No data for selected device")
        return
    print("Device parameters for LOINC " + data[6] + ": \n Component: " + data[7] + "\n Kind of property: " + data[4] +
          "\n Time aspect: " + data[1] + "\n System: " + data[2] + "\n Type of scale: " + data[
              3] + "\n Type of method: " +
          data[5] + "\n Unit: " + data[8])


def navigate():
    print("What do you want to do? (Enter the number for the selected action) \n 1 - set patient id "
          "\n 2 - connect new device \n 3 - pair device with patient \n 4 - disconnect device \n"
          " 5 - disconnect from all devices \n 6 - get current patient data \n 7 - get device description")
    choice = input(">>")
    if choice == "1":
        set_patient_id()
    elif choice == "2":
        connect_new_device()
    elif choice == "3":
        pair_with_patient()
    elif choice == "4":
        disconnect_device()
    elif choice == "5":
        disconnect_from_all_devices()
    elif choice == "6":
        get_patient_data()
    elif choice == "7":
        get_device_description()
    elif choice == '':
        return
    else:
        print("Please enter number from 1 to 5")


def main():
    try:
        get_doctor_id()
        while True:
            navigate()
    finally:
        disconnect_from_all_devices()


if __name__ == "__main__":
    main()
