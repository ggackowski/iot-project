import threading

import paho.mqtt.client as mqtt

hospital_hash = "clinic1234"
doctor_id = ""
patient_id = ""
mqttc = mqtt.Client(hospital_hash + "menager")
devices_types = []
devices_ids = []


def on_connect(client, user_data, flags, rc):
    print("Connected with result code " + str(rc))


def find_and_remove(device_id):
    idx = devices_ids.index(device_id)
    del devices_ids[idx]
    del devices_types[idx]


def on_message(client, userdata, msg):
    command = msg.topic
    comm_tab = command.split('/')

    first_part = comm_tab[0]
    sec_part = comm_tab[1]
    if first_part == hospital_hash:
        if sec_part == "add":
            # print("Available device: "+str(msg.payload)[2:-1]+"\n Do you want to connect to device? (Y/N)")
            device_hash = str(msg.payload)[2:-1]
            # TODO
            # add database connection
            device_id = 123456
            mqttc.publish(hospital_hash + "/" + device_hash, device_id, 0, False)
            mqttc.unsubscribe(hospital_hash + "/add")
            print("Added new device with id " + str(device_id))
        else:
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
                else:
                    print("Incorrect input: " + answer)
                    return
            else:
                if len(comm_tab) == 4:
                    fourth_part = comm_tab[3]
                    if fourth_part == "patient" and str(msg.payload)[2:-1] == "OK":
                        print("Patient " + patient_id + " connected to device " + sec_part)
                        mqttc.unsubscribe(msg.topic)
                    if fourth_part == "measure":
                        measurement = str(msg.payload)[2:-1]
                        print("Measurement from " + sec_part + " : " + measurement)
                        # TODO
                        # save measurement in database
                    if fourth_part == "unpair" and (
                            str(msg.payload)[2:-1] == "OK" or str(msg.payload)[2:-1] == "unpairdev"):
                        print("Disconnected from device " + sec_part + " id: " + third_part)
                        # TODO
                        # make device available in database
                        mqttc.unsubscribe(msg.topic)
                        mqttc.unsubscribe(hospital_hash + "/" + sec_part + "/" + third_part + "/measure")
                        find_and_remove(third_part)
                        if str(msg.payload)[2:-1] == "unpair":
                            mqttc.publish(msg.topic, "OK", 0, False)
                elif len(comm_tab) == 3 and str(msg.payload)[2:-1] == "OK":
                    # TODO
                    # save in database that device is not available
                    print("Connected to device " + sec_part + " id: " + third_part)
                    devices_types.append(sec_part)
                    devices_ids.append(third_part)


def configure():
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.connect("127.0.0.1", 1883, 60)
    mqttc.loop_forever()


def get_doctor_id():
    global doctor_id
    print("Welcome to Smart Medical Devices Management System!")
    print("Please enter your doctor id:")
    doctor_id = input(">>")


def set_patient_id():
    global patient_id
    print("Please enter patient id:")
    patient_id = input(">>")
    print("Current patient id: " + patient_id)


def connect_new_device():
    # TODO
    # add getting available types of devices from database
    available_devices = ["1"]
    print("Available devices:")
    i = 0
    for device in available_devices:
        print(str(i) + " - " + device)
        i += 1
    print("Please select number for device")
    number = int(input(">> "))
    if 0 <= number < i:
        device_type = available_devices[number]
    else:
        print("Invalid device number")
        return
    mqttc.subscribe(hospital_hash + "/" + device_type + "/pair")


def pair_with_patient():
    if patient_id == "":
        print("Please set patient id first")
        return
    print("Connected devices:")
    for i in range(0, len(devices_ids)):
        print(str(i) + " - Type: " + devices_types[i] + ", id: " + devices_ids[i])
    print("Please select number for device")
    number = int(input(">> "))
    if 0 <= number < len(devices_ids):
        device_type = devices_types[number]
        device_id = devices_ids[number]
    else:
        print("Invalid device number")
        return
    mqttc.publish(hospital_hash + "/" + device_type + "/" + device_id + "/patient", patient_id, 0, False)
    mqttc.subscribe(hospital_hash + "/" + device_type + "/" + device_id + "/patient")
    mqttc.subscribe(hospital_hash + "/" + device_type + "/" + device_id + "/measure")


def disconnect_device():
    print("Connected devices:")
    for i in range(0, len(devices_ids)):
        print(str(i) + " - Type: " + devices_types[i] + ", id: " + devices_ids[i])
    print("Please select number for device")
    number = int(input(">> "))
    if 0 <= number < len(devices_ids):
        device_type = devices_types[number]
        device_id = devices_ids[number]
    else:
        print("Invalid device number")
        return
    mqttc.publish(hospital_hash + "/" + device_type + "/" + device_id + "/unpair", "unpair", 0, False)


def add_to_database():
    mqttc.subscribe(hospital_hash + "/add")


def navigate():
    print("What do you want to do? (Enter the number for the selected action) \n 1 - set patient id "
          "\n 2 - connect new device \n 3 - pair device with patient \n 4 - disconnect device \n "
          "5 - add new device to database")
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
        add_to_database()
    else:
        print("Please enter number from 1 to 5")


def run_mqtt():
    thread = threading.Thread(target=configure)
    thread.start()


def main():
    get_doctor_id()
    run_mqtt()
    while True:
        navigate()


if __name__ == "__main__":
    main()
