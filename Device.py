import uuid

class Device:
    def __init__(self, loinc_num = None, patient_id = None, doctor_id = None, data_loinc_num = None, id = uuid.uuid1()):
        self._loinc_num = loinc_num
        self._patient_id = patient_id
        self._doctor_id = doctor_id
        self._data_loinc_num = data_loinc_num
        self._id = id

    @property
    def loinc_num(self):
        return self._loinc_num

    @loinc_num.setter
    def loinc_num(self, loinc_number):
        self._loinc_num = loinc_number

    @property
    def patient_id(self):
        return self._patient_id

    @patient_id.setter
    def patient_id(self, patient_identifier):
        self._patient_id = patient_identifier

    @property
    def doctor_id(self):
        return self._doctor_id

    @doctor_id.setter
    def doctor_id(self, doctor_identifier):
        self._doctor_id = doctor_identifier

    @property
    def data_loinc_num(self):
        return self._data_loinc_num

    @data_loinc_num.setter
    def data_loinc_number(self, data_from_loinc_number):
        self._data_loinc_num = data_from_loinc_number

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, identifier):
        self._id = identifier

    def create(self, loinc_num, data_loinc_num):
        "Send to 'hospital_hash/add' topic parameteres to manager"


    def pair(self):
        '''Send to hospital_hash/this.type_of_device/pair to manager payload = this.id
        listen to hospital_hash/this.type_of_device/this.id payload = doctor_id
        Send to hospital_hash/this.type_of_device/this.id payload = 'OK' '''


    def unpair(self):
        '''Send to hospital_hash/this.type_of_device/id/unpair payload = OK
            Listen on message hospital_hash/this.type_of_device/id/unpair payload = OK
            and next unsubscribe?
        '''


    def measure(self):
        '''
        Make measurement
        Send measurement to hospital_hash/this.type_of_device/id/measure payload = detail of measurement
        listen to confirmation and print it
        '''

    def switch_patient(self):
        '''
        Listen to hospital_hash/doctor_id payload = patient_id
        Change this.patient_id
        Send confirmation to manager
        '''
