import paho.mqtt.client as mqtt
import db.db as db_manager

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
    mqttc.publish(hospital_hash + "/" + device_hash, device_id, 0, False)


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
