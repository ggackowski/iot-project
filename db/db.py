import psycopg2
import psycopg2.extras

DB_HOST = "localhost"
DB_NAME = "iot_db"
DB_USER = "postgres"
DB_PASS = "1234"

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


class PairError(Exception):
    def __init__(self, msg):
        self.msg = msg


def modifying_db_exception_block(func):
    """decorator that commits changes done to db by the 'func' and wraps it in try/except block"""

    def inner(*args):
        try:
            func(*args)
            conn.commit()
            print(f"{func.__name__}{args} executed successfully")
        except PairError as pe:
            print(pe)
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
def add_device(name, loinc_num, mac):
    cur.execute("INSERT INTO devices (name, loinc_num, mac) VALUES(%s, %s, %s)", (name, loinc_num, mac))


@modifying_db_exception_block
def add_measurement(val, device_id, patient_id):
    cur.execute("INSERT INTO measurements (val, device_id, patient_id) VALUES(%s, %s, %s)",
                (val, device_id, patient_id))


# DELETE
@modifying_db_exception_block
def delete_doctor(d_id):
    cur.execute("DELETE FROM doctors WHERE id=%s", (d_id,))


@modifying_db_exception_block
def delete_patient(p_id):
    cur.execute("DELETE FROM patients WHERE id=%s", (p_id,))


@modifying_db_exception_block
def delete_device(d_id):
    cur.execute("DELETE FROM devices WHERE id=%s", (d_id,))


@modifying_db_exception_block
def delete_measurement(m_id):
    cur.execute("DELETE FROM measurements WHERE id=%s", (m_id,))


@modifying_db_exception_block
def delete_patient_measurements(p_id):
    cur.execute("DELETE FROM measurements WHERE patient_id=%s", (p_id,))


@modifying_db_exception_block
def delete_device_measurements(d_id):
    cur.execute("DELETE FROM measurements WHERE device_id=%s", (d_id,))


# PAIR/UNPAIR
@modifying_db_exception_block
def pair_device_to_doctor(device_id, doctor_id):
    cur.execute("SELECT id FROM devices WHERE id = %s AND taken = FALSE", (device_id,))
    if cur.fetchone() is None:
        raise PairError("CAN'T PAIR DEVICE TO DOCTOR, DEVICE TAKEN OR DEVICE ID DOESN'T EXISTS IN DB")
    cur.execute("UPDATE devices "
                "SET taken = TRUE, doctor_id = %s "
                "WHERE id = %s AND taken = FALSE", (doctor_id, device_id))


@modifying_db_exception_block
def pair_device_to_patient(d_id, p_id):
    cur.execute("SELECT id FROM devices WHERE id = %s AND taken = TRUE", (d_id,))
    if cur.fetchone() is None:
        raise PairError("CAN'T PAIR DEVICE TO PATIENT, DEVICE NOT TAKEN OR DEVICE ID DOESN'T EXISTS IN DB")
    cur.execute("UPDATE devices "
                "SET patient_id = %s "
                "WHERE id = %s AND taken = TRUE", (p_id, d_id))


@modifying_db_exception_block
def unpair_device_from_doctor(device_id, doctor_id):
    cur.execute("SELECT id FROM devices WHERE id = %s AND doctor_id = %s AND taken = TRUE", (device_id, doctor_id))
    if cur.fetchone() is None:
        raise PairError(
            "CAN'T UNPAIR DEVICE FROM DOCTOR, DEVICE NOT PAIRED WITH THE DOCTOR OR DEVICE ID DOESN'T EXISTS IN DB")
    cur.execute("UPDATE devices "
                "SET doctor_id = NULL, taken = FALSE "
                "WHERE id = %s AND doctor_id = %s AND taken = TRUE", (device_id, doctor_id))


@modifying_db_exception_block
def unpair_device_from_patient(d_id, p_id):
    cur.execute("SELECT id FROM devices WHERE id = %s AND patient_id = %s AND taken = TRUE", (d_id, p_id))
    if cur.fetchone() is None:
        raise PairError(
            "CAN'T UNPAIR DEVICE FROM PATIENT, DEVICE NOT PAIRED WITH PATIENT OR DEVICE ID DOESN'T EXISTS IN DB")
    cur.execute("UPDATE devices "
                "SET patient_id = NULL "
                "WHERE id = %s AND patient_id = %s AND taken = TRUE", (d_id, p_id))


# GET
def get_from_db_exception_block(func):
    """decorator that returns the results of the 'func' as a list of dicts (psycopg2.extras.DictRow)
    or a dict/None if know that there will always be at most one result, and wraps it in the try/except block"""

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
def get_free_devices():
    cur.execute("SELECT * FROM devices WHERE taken = FALSE")
    return cur.fetchall()


@get_from_db_exception_block
def get_devices_paired_to_doctor(d_id):
    cur.execute("SELECT * FROM devices WHERE doctor_id = %s", (d_id,))
    return cur.fetchall()


@get_from_db_exception_block
def get_device_from_mac(mac):
    cur.execute("SELECT * FROM devices WHERE mac = %s", (mac,))
    return cur.fetchone()


@get_from_db_exception_block
def get_doctor_by_device_id(d_id):
    cur.execute("SELECT doctors.* FROM doctors "
                "INNER JOIN devices ON devices.doctor_id = doctors.id "
                "WHERE devices.doctor_id = %s", (d_id,))
    return cur.fetchone()


if __name__ == '__main__':
    delete_db()
    init_db()
    add_doctor("d", "o")
    add_patient("p", "a")
    add_device("name", "loinc", "mac")
    add_device("name", "loinc", "mac")
    print(get_free_devices())

    pair_device_to_doctor(1, 1)
    print(get_devices_paired_to_doctor(1))
    print(get_doctor_by_device_id(1))

    pair_device_to_patient(1, 1)
    unpair_device_from_patient(1, 1)
    unpair_device_from_doctor(1, 1)

    add_measurement(1.5, 1, 1)
    add_doctor("hi", "t")
    delete_doctor(2)

    disconnect()
