import paho.mqtt.client as mqtt
import db.db as db_manager
import csv

hospital_hash = "clinic1234"
mqttc = mqtt.Client(hospital_hash + "devices_manager")


def on_connect(client, user_data, flags, rc):
    print("Connected with result code " + str(rc))
    mqttc.subscribe(hospital_hash + "/add")


def on_message(client, userdata, msg):
    device_data = str(msg.payload)[2:-1]
    data_tab = device_data.split('#')
    device_hash = data_tab[0]
    loinc = data_tab[1]
    name = data_tab[2]
    device = db_manager.get_device_from_mac(device_hash)
    if device is None:
        db_manager.add_device(name, loinc, device_hash)
        device_id = db_manager.get_device_from_mac(device_hash)[0]
        print("Added new device with id " + str(device_id))
    else:
        device_id = device[0]
    loinc_data = db_manager.get_loinc_data(loinc)
    if loinc_data is None:
        data = get_data_from_csv(loinc)
        db_manager.add_loinc_data(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7])
    mqttc.publish(hospital_hash + "/" + device_hash, device_id, 0, False)


def get_data_from_csv(loinc):
    csv_file = csv.reader(open("Loinc.csv", "r"), delimiter= ",")
    for row in csv_file:
        if row[0] == loinc:
            return row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[26]

def run_mqtt():
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.connect("127.0.0.1", 1883, 60)
    mqttc.loop_forever()


def main():
    print("Welcome to device manager!")
    run_mqtt()


if __name__ == "__main__":
    main()
