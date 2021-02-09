from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import time
import json
import random


class Device:
    connectReqJson = '{"state": {"desired": {"status": "connected"}, "reported": {"status": "connected"}}}'
    test = '{"halo": 1}'

    def __init__(self, private_key, certificate, client_id, endpoint, device_name, parameters):
        self.shadowClient = AWSIoTMQTTShadowClient(client_id)
        self.configure_shadow_client(endpoint, private_key, certificate)
        self.shadowClient.connect()
        self.configure_device_shadow(device_name)
        self.parameters = parameters
        self.deviceShadow.shadowUpdate(self.connectReqJson, self.on_shadow_update, 5)
        self.deviceShadow.shadowRegisterDeltaCallback(self.on_delta_update)
        self.execute_user_input()

    def on_delta_update(self, payload, response_status, token):
        print('delta update')
        data = json.loads(payload)
        print(data)
        data = data['state']
        if 'status' in data and data['status'] == 'paired' and 'doctor_id' in data and 'patient_id' in data:
            pairedJson = '{"state": {"reported": {"status": "paired", "patient_id": ' + str(
                data['patient_id']) + ', "doctor_id": ' + str(data['doctor_id']) + '}}}'
            print('pair')
            print(pairedJson)
            self.deviceShadow.shadowUpdate(pairedJson, self.on_shadow_update, 5)

        elif 'patient_id' in data:
            print('patient id')
            patientIdJson = '{"state": {"reported": {"patient_id": ' + str(data['patient_id']) + '}}}'
            self.deviceShadow.shadowUpdate(patientIdJson, self.on_shadow_update, 5)

        elif 'status' in data and data['status'] == 'connected':  # and data['doctor_id'] == -1 and data['patient_id'] == -1:
            connectJson = '{"state": {"reported": {"status": "connected", "patient_id": -1, "doctor_id": -1}, ' \
                          '"desired": {"status": "connected", "patient_id": -1, "doctor_id": -1}}} '
            self.deviceShadow.shadowUpdate(connectJson, self.on_shadow_update, 5)

    def configure_shadow_client(self, endpoint, private_key, certificate):
        self.shadowClient.configureEndpoint(endpoint, 8883)
        self.shadowClient.configureCredentials("../../../certificates/Amazon_Root_CA_1.pem", private_key,
                                               certificate)
        self.shadowClient.configureConnectDisconnectTimeout(10)
        self.shadowClient.configureMQTTOperationTimeout(5)

    def configure_device_shadow(self, device_name):
        self.deviceShadow = self.shadowClient.createShadowHandlerWithName(device_name, True)
        self.deviceShadow.shadowGet(self.on_shadow_get, 5)

    def on_shadow_update(self, payload, response_status, token):
        pass

    @staticmethod
    def on_shadow_get(payload, response_status, token):
        print('get')
        print(payload)

    def measure(self):
        min = self.parameters['minimal_measurement']
        max = self.parameters['maximal_measurement']
        value = random.randint(min, max)
        measureJson = '{"state": {"desired": {"indication": ' + str(value) + '}}}'
        self.deviceShadow.shadowUpdate(measureJson, self.on_shadow_update, 5)

    def unpair(self):
        unpairJson = ' {"state": {"desired": {"status": "disconnected"}}}'
        self.deviceShadow.shadowUpdate(unpairJson, self.on_shadow_update, 5)

    def execute_user_input(self):
        while True:
            text = input("\n>> ")
            # if text == "pair":
            #     pair()
            if text == "measure":
                self.measure()
            if text == "disconnect":
                self.unpair()

# if __name__ == '__main__':
#     device = Device("../../../config/glucometer_2339_0/0ee175d973-private.pem.key",
#                     "../../config/glucometer_2339_0/0ee175d973-certificate.pem.crt",
#                     "glucometer_17432f61", "a196zks8gm1dr-ats.iot.us-east-1.amazonaws.com", "glucometer_17432f61")
