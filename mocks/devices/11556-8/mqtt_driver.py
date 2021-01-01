import paho.mqtt.client as mqtt
import logging
import threading
import time

topics = {
    "send_device_data": "",
    "get_id": "",
    "send_pair_request": "",
    "get_doctor_id": "",
    "send_pair_confirm": "",
    "get_patient_id": "",
    "send_setting_patient_confirm": "",
    "send_measurement": "",
    "send_unpair_request": "",
    "get_unpair_request": "",
    "send_unpair_confirm": "",
    "get_unpair_confirm": ""
}

subscribed_topic_names = []

hospital_hash = "xxxxxxxxx"
device_type = "x"
device_hash = "xxxx"
device_id = "xxxxx"
doctor_id = "xx"
patient_id = "xx"

client = mqtt.Client()

def set_hospital_hash(hash):
    global hospital_hash
    hospital_hash = hash

def set_device_type(Type):
    global device_type
    device_type = Type

def set_device_hash(hash):
    global device_hash
    device_hash = hash

def set_device_id(Id):
    global device_id
    device_id = Id

def run():
    set_initial_topic_names()
    run_mqtt()

def set_initial_topic_names():
    topics["send_device_data"] = hospital_hash + "\\add"
    topics["get_id"] = hospital_hash + "\\hash"
    topics["send_pair_request"] = hospital_hash + "\\" + device_type + "\\pair"

def set_topic_names_after_receiving_device_id():
    topics["get_doctor_id"] = hospital_hash + "\\" + device_type + "\\" + device_id
    topics["send_pair_confirm"] = hospital_hash + "\\" + device_type + "\\" + device_id
    topics["get_patient_id"] = hospital_hash + "\\" + device_type + "\\" + device_id + "\\patient"
    topics["send_setting_patient_confirm"] = hospital_hash + "\\" + device_type + "\\" + device_id + "\\patient"
    topics["send_measurement"] = hospital_hash + "\\" + device_type + "\\" + device_id + "\\measure"
    topics["send_unpair_request"] = hospital_hash + "\\" + device_type + "\\" + device_id + "\\unpair"
    topics["get_unpair_request"] = hospital_hash + "\\" + device_type + "\\" + device_id + "\\unpair"
    topics["send_unpair_confirm"] = hospital_hash + "\\" + device_type + "\\" + device_id + "\\unpair"
    topics["get_unpair_confirm"] = hospital_hash + "\\" + device_type + "\\" + device_id + "\\unpair"

def send_device_data_to_manager():
    global device_hash
    print("sending " + topics["send_device_data"] + " " + device_hash)
    client.publish(topics["send_device_data"], device_hash, 0, False)

def send_pair_request():
    global device_id
    print("sending " + topics["send_pair_request"] + " " + device_id)
    client.publish(topics["send_pair_request"], device_id, 0, False)

def send_pair_confirm():
    print("sending " + topics["send_pair_confirm"] + " OK")
    print("[pairing finished]\n>> ")
    client.publish(topics["send_pair_confirm"], "OK", 0, False)

def send_setting_patient_confirm():
    print("sending " + topics["send_setting_patient_confirm"] + " OK")
    print("[patient id set]\n>> ")
    client.publish(topics["send_setting_patient_confirm"], "OK", 0, False)

def send_measurement(measurement):
    print("sending " + topics["send_measurement"] + " " + measurement)
    client.publish(topics["send_measurement"], measurement, 0, False)

def send_unpair_request():
    print("sending " + topics["send_unpair_request"] + " unpair")
    client.publish(topics["send_unpair_request"], "unpair", 0, False)

def send_unpair_confirm():
    print("sending " + topics["send_unpair_confirm"] + " OK")
    print("[device unpaired\n>> ")
    client.publish(topics["send_unpair_confirm"], "OK", 0, False)

def run_mqtt():
    thread = threading.Thread(target=run_mqtt_in_background)
    thread.start()

def set_mqtt_subscriptions_to_state__add_to_database():
    global client
    unsubscribe_all_topics()
    client.subscribe(topics["get_id"])
    subscribed_topic_names.append("get_id")

def set_mqtt_subscriptions_to_state__pair():
    global client
    unsubscribe_all_topics()
    client.subscribe(topics["get_doctor_id"])
    subscribed_topic_names.append("get_doctor_id")

def set_mqtt_subscriptions_to_state__set_patient():
    global client
    unsubscribe_all_topics()
    client.subscribe(topics["get_patient_id"])

def set_mqtt_subscriptions_to_state__unpair():
    global client
    unsubscribe_all_topics()
    client.subscribe(topics["get_unpair_request"]) 
    subscribed_topic_names.append("get_unpair_request")

def on_message(client, userdata, msg):
    if msg.topic == topics["get_id"]:
        on_get_id_messsage(msg)
    elif msg.topic == topics["get_doctor_id"]:
        on_get_doctor_id_message(msg)
    elif msg.topic == topics["get_patient_id"]:
        on_get_patient_id_message(msg)
    elif msg.topic == topics["get_unpair_request"]:
        on_get_unpair_request(msg)
    

def on_get_id_messsage(msg):
    global device_id
    payload = get_payload_content(msg)
    if is_hash_from_payload_equal_device_hash(payload):
        device_id = payload.rsplit('#', 1)[0]
        set_topic_names_after_receiving_device_id()
        print("[device id set]\n>> ")
        unsubscribe_all_topics()

def on_get_doctor_id_message(msg):
    global doctor_id
    payload = get_payload_content(msg)
    doctor_id = payload
    unsubscribe_all_topics()
    send_pair_confirm()
    set_mqtt_subscriptions_to_state__set_patient()

def on_get_patient_id_message(msg):
    global patient_id
    payload = get_payload_content(msg)
    if (payload == "OK"):
        return
    patient_id = payload
    send_setting_patient_confirm()

def on_get_unpair_request(msg):
    if (get_payload_content(msg) == "OK"):
        return
    send_unpair_confirm()

def get_payload_content(msg):
    return str(msg.payload)[2:-1]

def is_hash_from_payload_equal_device_hash(payload):
    return payload.rsplit('#', 1)[1] == device_hash

def unsubscribe_all_topics():
    for name in subscribed_topic_names:
        client.unsubscribe(topics[name])   

def run_mqtt_in_background():
    global client
    client.connect("127.0.0.1", 1883, 60)
    client.on_message = on_message
    client.loop_forever()
    