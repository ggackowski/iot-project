from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import time
import json


def on_shadow_update(payload, response_status, token):
    print(payload)
    print(response_status)
    print(token)


class Device:

    def __init__(self, private_key, certificate, client_id, endpoint, device_name):
        self.shadowClient = AWSIoTMQTTShadowClient(client_id)
        self.shadowClient.configureEndpoint(endpoint, 8883)
        self.shadowClient.configureCredentials("../iot-project/certificates/Amazon_Root_CA_1.pem", private_key,
                                               certificate)
        self.shadowClient.configureConnectDisconnectTimeout(10)
        self.shadowClient.configureMQTTOperationTimeout(5)
        self.shadowClient.connect()
        self.deviceShadow = self.shadowClient.createShadowHandlerWithName(device_name, True)
        self.deviceShadow.shadowGet(self.on_shadow_get, 5)

    @staticmethod
    def on_shadow_get(payload, response_status, token):
        print(payload)
        print(response_status)
        print(token)


if __name__ == '__main__':
    device = Device("../iot-project/certificates/glucometer_2339_0/0ee175d973-private.pem.key",
                    "../iot-project/certificates/glucometer_2339_0/0ee175d973-certificate.pem.crt",
                    "glucometer_17432f61", "a196zks8gm1dr-ats.iot.us-east-1.amazonaws.com", "glucometer_17432f61")
    while True:
        time.sleep(1)
