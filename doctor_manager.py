import threading
import random
import string

import paho.mqtt.client as mqtt
import db.db as db_manager
from datetime import datetime

hospital_hash = "clinic1234"
doctor_id = ""
patient_id = ""
mqttc = mqtt.Client(
    hospital_hash + "doctor_manager" + random.choice(string.ascii_letters) + random.choice(string.ascii_letters))


def on_connect(client, user_data, flags, rc):
    print("Connected with result code " + str(rc))


def on_message(client, userdata, msg):
    command = msg.topic
    comm_tab = command.split('/')

    first_part = comm_tab[0]
    sec_part = comm_tab[1]
    if first_part == hospital_hash:
        third_part = comm_tab[2]
        if third_part == "pair":
            device_id = str(msg.payload)[2:-1]
            print("Do you want to connect with " + sec_part + " with id " + device_id + "? (Y/N)")
            answer = input(">> ")
            if answer == 'Y' or answer == 'y':
                mqttc.publish(hospital_hash + "/" + sec_part + "/" + device_id, doctor_id, 0, False)
                mqttc.subscribe(hospital_hash + "/" + sec_part + "/" + device_id)
                mqttc.subscribe(hospital_hash + "/" + sec_part + "/" + device_id + "/unpair")
                mqttc.unsubscribe(hospital_hash + "/" + sec_part + "/pair")
            elif answer != 'N' or answer != 'n':
                print("Incorrect input: " + answer)
                return
        else:
            if len(comm_tab) == 4:
                fourth_part = comm_tab[3]
                if fourth_part == "patient" and str(msg.payload)[2:-1] == "OK":
                    print("Patient " + str(patient_id) + " connected to device " + sec_part)
                    db_manager.pair_device_to_patient(third_part, patient_id)
                    mqttc.unsubscribe(msg.topic)
                if fourth_part == "measure":
                    measurement = str(msg.payload)[2:-1]
                    measurement_table = measurement.split("#")
                    measurement_data = measurement_table[0]
                    unit_number = measurement_table[1]
                    print("Measurement from " + sec_part + " : " + measurement_data)
                    db_manager.add_measurement(measurement_data, third_part, patient_id, datetime.now(), unit_number)
                if fourth_part == "unpair" and (
                        str(msg.payload)[2:-1] == "OK" or str(msg.payload)[2:-1] == "unpairdev"):
                    print("Disconnected from device " + sec_part + " id: " + third_part)
                    if patient_id != "":
                        db_manager.unpair_device_from_patient(third_part, patient_id)
                    db_manager.unpair_device_from_doctor(third_part, doctor_id)
                    mqttc.unsubscribe(msg.topic)
                    mqttc.unsubscribe(hospital_hash + "/" + sec_part + "/" + third_part + "/measure")
                    if str(msg.payload)[2:-1] == "unpairdev":
                        mqttc.publish(msg.topic, "OK", 0, False)
            elif len(comm_tab) == 3 and str(msg.payload)[2:-1] == "OK":
                print("Connected to device " + sec_part + " id: " + third_part)
                db_manager.pair_device_to_doctor(third_part, doctor_id)


def configure():
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.connect("broker.hivemq.com", 1883, 60)
    mqttc.loop_forever()


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


def connect_new_device():
    results = db_manager.get_free_devices()
    available_devices = []
    if not results:
        print("No devices available")
        return
    for result in results:
        if result[1] not in available_devices:
            available_devices.append(result[1])
    print("Available devices:")
    i = 0
    for device in available_devices:
        print(str(i) + " - " + device)
        i += 1
    print("Please select number for device")
    number = int(input(">> "))
    if 0 <= number < i:
        device_loinc = results[number][2]
    else:
        print("Invalid device number")
        return
    mqttc.subscribe(hospital_hash + "/" + device_loinc + "/pair")


def pair_with_patient():
    if patient_id == '':
        print("Set patient id first!")
        return
    results = db_manager.get_devices_paired_to_doctor(doctor_id)
    connected_devices = []
    i = 0
    if not results:
        print("No devices connected with doctor")
        return
    for result in results:
        connected_devices.append(str(i) + " - " + str(result[0]) + ", " + result[1] + ", " + result[2])
        i += 1
    print("Connected devices:")
    for device in connected_devices:
        print(device)
    print("Please select number for device")
    number = int(input(">> "))
    if 0 <= number < len(connected_devices):
        device_loinc = results[number][2]
        device_mac = results[number][3]
    else:
        print("Invalid device number")
        return
    mqttc.publish(hospital_hash + "/" + device_loinc + "/" + device_mac + "/patient", patient_id, 0, False)
    mqttc.subscribe(hospital_hash + "/" + device_loinc + "/" + device_mac + "/patient")
    mqttc.subscribe(hospital_hash + "/" + device_loinc + "/" + device_mac + "/measure")


def disconnect_device():
    results = db_manager.get_devices_paired_to_doctor(doctor_id)
    connected_devices = []
    i = 0
    if not results:
        print("No devices connected with doctor")
        return
    for result in results:
        connected_devices.append(str(i) + " - " + str(result[0]) + " " + result[1] + " " + result[2])
        i += 1
    print("Connected devices:")
    for device in connected_devices:
        print(device)
    print("Please select number for device")
    number = int(input(">> "))
    if 0 <= number < len(connected_devices):
        device_loinc = results[number][2]
        device_mac = results[number][3]
    else:
        print("Invalid device number")
        return
    mqttc.publish(hospital_hash + "/" + device_loinc + "/" + device_mac + "/unpair", "unpair", 0, False)


def disconnect_from_all_devices():
    results = db_manager.get_devices_paired_to_doctor(doctor_id)
    if results:
        for result in results:
            mqttc.publish(hospital_hash + "/" + result[1] + "/" + result[3] + "/unpair", "unpair", 0, False)


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


def run_mqtt():
    mqtt_thread = threading.Thread(target=configure)
    mqtt_thread.start()


def main():
    get_doctor_id()
    run_mqtt()
    while True:
        navigate()


if __name__ == "__main__":
    main()
