import sys
sys.path.insert(0, '../')
from device import Device

DEVICE_PARAMETERS = {
    "loinc_num": "2339-0",
    "loinc_long_common_name": "Glucose [Mass/volume] in Blood",
    "hash": "17432f61-21c1-45c1-9759-07318bd07e4a",
    "minimal_measurement": 20,
    "maximal_measurement": 600,
    "unit": "mg/dL"
}

if __name__ == "__main__":
    device = Device("../../../config/glucometer_2339_0/0ee175d973-private.pem.key",
                "../../../config/glucometer_2339_0/0ee175d973-certificate.pem.crt",
                "glucometer_17432f61", "a196zks8gm1dr-ats.iot.us-east-1.amazonaws.com", "glucometer_17432f61", DEVICE_PARAMETERS)



