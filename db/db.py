import psycopg2
import psycopg2.extras
import os

# using environment variables to get db host and password
DB_HOST = os.environ.get("iot_db_host")
DB_PASS = os.environ.get("iot_db_pass")
DB_NAME = "postgres"
DB_USER = "postgres"

conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


def init_db(path="init_db.sql"):
    """creates tables from the sql file located at path"""
    with open(path, "r") as f:
        cur.execute(f.read())
        conn.commit()
    print("INITIALIZATION SUCCESSFUL")


def delete_db():
    """drops every table"""
    try:
        query = "DROP SCHEMA public CASCADE;" \
                "CREATE SCHEMA public;" \
                "GRANT ALL ON SCHEMA public TO postgres;" \
                "GRANT ALL ON SCHEMA public TO public;"
        cur.execute(query)
        conn.commit()
        print("DB DELETED SUCCESSFULLY")
    except (Exception, psycopg2.Error) as error:
        print("ERROR WHILE DELETING DB:")
        print(error)


def disconnect():
    """closes the connection with db. CALL THIS AFTER YOU NO LONGER NEED DB OR atexit"""
    try:
        cur.close()
        conn.close()
        print("DISCONNECTED SUCCESSFULLY")
    except (Exception, psycopg2.Error) as error:
        print("ERROR WHILE DISCONNECTING:")
        print(error)


class ModifyingError(Exception):
    def __init__(self, msg):
        self.msg = msg


def modifying_db_exception_block(func):
    """decorator that commits changes done to db by the 'func' and wraps it in try/except block"""

    def inner(*args):
        try:
            func(*args)
            conn.commit()
            print(f"{func.__name__}{args} executed successfully")
        except ModifyingError as me:
            print(me)
        except (Exception, psycopg2.Error) as error:
            print(f"ERROR WHILE EXECUTING {func.__name__}{args}:")
            print(error)

    return inner


# ADD
@modifying_db_exception_block
def add_doctor(name, surname):
    cur.execute("INSERT INTO doctors (name, surname) VALUES(%s, %s)", (name, surname))


@modifying_db_exception_block
def add_patient(name, surname):
    cur.execute("INSERT INTO patients (name, surname) VALUES(%s, %s)", (name, surname))


@modifying_db_exception_block
def add_measurement(val, device_id, patient_id, date):
    cur.execute("INSERT INTO measurements (val, device_id, patient_id, date) VALUES(%s, %s, %s, %s)",
                (val, device_id, patient_id, date))


@modifying_db_exception_block
def add_loinc_data(loinc, component, property, time, system, scale_type, method_type, unit):
    cur.execute("INSERT INTO loinc_data (time, system, scale_typ, property, method_typ, loinc_num, component, unit)" +
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (time, system, scale_type, property, method_type, loinc, component, unit))


@modifying_db_exception_block
def add_device(name, loinc_number, uuid, unit, minimum_indication, maximum_indication):
    cur.execute("INSERT INTO devices (name, loinc_number, uuid, unit, minimum indication, maximum indication) "
                "VALUES (%s, %s, %s, %s, %s, %s)", (name, loinc_number, uuid, unit, minimum_indication,
                                                    maximum_indication,))


# DELETE
@modifying_db_exception_block
def delete_doctor(d_id):
    cur.execute("DELETE FROM doctors WHERE id=%s", (d_id,))


@modifying_db_exception_block
def delete_patient(p_id):
    cur.execute("DELETE FROM patients WHERE id=%s", (p_id,))


@modifying_db_exception_block
def delete_device(d_id):
    cur.execute("SELECT * FROM devices WHERE uuid = %s", (d_id,))


@modifying_db_exception_block
def delete_measurement(m_id):
    cur.execute("DELETE FROM measurements WHERE id=%s", (m_id,))


@modifying_db_exception_block
def delete_patient_measurements(p_id):
    cur.execute("DELETE FROM measurements WHERE patient_id=%s", (p_id,))


@modifying_db_exception_block
def delete_device_measurements(d_id):
    cur.execute("DELETE FROM measurements WHERE device_id=%s", (d_id,))


# DEVICE HISTORY
@modifying_db_exception_block
def start_device_history(device_id, patient_id, doctor_id, start_date):
    cur.execute("INSERT INTO device_history (device_id, patient_id, doctor_id, start_date, end_date) "
                "VALUES(%s, %s, %s, %s, NULL)", (device_id, patient_id, doctor_id, start_date))


@modifying_db_exception_block
def add_end_date_to_history(device_id, patient_id, doctor_id, end_date):
    cur.execute("UPDATE device_history SET end_date = %s WHERE device_id = %s AND "
                "patient-id = %s AND doctor_id=%s AND end_date=NULL", (end_date, device_id, patient_id, doctor_id))


# GET
def get_from_db_exception_block(func):
    """decorator that returns the results of the 'func' as a list of dicts (psycopg2.extras.DictRow)
    or a dict/None if we know that there will always be at most one result, and wraps it in the try/except block"""

    def inner(*args):
        try:
            result = func(*args)
            if not result:
                print(f"NO RESULTS FROM {func.__name__}{args}")
            print(f"{func.__name__} executed successfully")
            return result
        except (Exception, psycopg2.Error) as error:
            print(f"ERROR WHILE EXECUTING {func.__name__}{args}:")
            print(error)

    return inner


@get_from_db_exception_block
def get_all_devices():
    cur.execute("SELECT * FROM devices")
    return cur.fetchall()


@get_from_db_exception_block
def get_device_from_uuid(mac):
    cur.execute("SELECT * FROM devices WHERE uuid = %s", (mac,))
    return cur.fetchone()


@get_from_db_exception_block
def get_device_from_name(name):
    cur.execute("SELECT * FROM devices WHERE name = %s", (name,))
    return cur.fetchone()


@get_from_db_exception_block
def get_doctor_id(name, surname):
    cur.execute("SELECT * FROM doctors WHERE name = %s and surname= %s", (name, surname,))
    return cur.fetchone()


@get_from_db_exception_block
def get_patient_id(name, surname):
    cur.execute("SELECT * FROM patients WHERE name = %s and surname= %s", (name, surname,))
    return cur.fetchone()


@get_from_db_exception_block
def get_patient_measurements(p_id):
    cur.execute("SELECT patients.name, patients.surname, measurements.val, devices.name, devices.loinc_num,"
                " measurements.date, devices.unit FROM patients "
                "INNER JOIN measurements ON measurements.patient_id = patients.id "
                "INNER JOIN devices ON measurements.device_id = devices.mac "
                "WHERE patients.id = %s", (p_id,))
    return cur.fetchall()


@get_from_db_exception_block
def get_loinc_data(loinc_num):
    cur.execute("SELECT loinc_data.* FROM loinc_data "
                "WHERE loinc_data.loinc_num = %s", (loinc_num,))
    return cur.fetchone()


@get_from_db_exception_block
def get_device_data(d_name):
    cur.execute("SELECT devices.* FROM devices "
                "WHERE devices.name = %s", (d_name,))
    return cur.fetchone()


@get_from_db_exception_block
def get_device_history(d_uuid):
    cur.execute("SELECT device_history.* FROM device_history WHERE device_history.device_id=%s", (d_uuid,))
    cur.fetchall()


if __name__ == '__main__':
    delete_db()
    init_db()
    disconnect()
