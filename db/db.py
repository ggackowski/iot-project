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
    def inner(*args):
        try:
            func(*args)
            conn.commit()
            print(f"{func.__name__} executed successfully")
        except PairError as pe:
            print(pe)
        except (Exception, psycopg2.Error) as error:
            print(f"ERROR WHILE EXECUTING {func.__name__}:")
            print(error)

    return inner


@modifying_db_exception_block
def add_doctor(name, surname):
    cur.execute("INSERT INTO doctors (name, surname) VALUES(%s, %s)", (name, surname))


@modifying_db_exception_block
def add_patient(name, surname):
    cur.execute("INSERT INTO patients (name, surname) VALUES(%s, %s)", (name, surname))


@modifying_db_exception_block
def add_device(name, loinc_num):
    cur.execute("INSERT INTO devices (name, loinc_num) VALUES(%s, %s)", (name, loinc_num))


@modifying_db_exception_block
def add_measurement(val, loinc_num, device_id, patient_id):
    cur.execute("INSERT INTO measurements (val, loinc_num, device_id, patient_id) VALUES(%s, %s, %s, %s)",
                (val, loinc_num, device_id, patient_id))


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


if __name__ == '__main__':
    delete_db()
    init_db()
    add_doctor("d", "o")
    add_patient("p", "a")
    add_device("name", "loinc")

    pair_device_to_doctor(1, 1)
    cur.execute("SELECT * FROM devices")
    print(cur.fetchall())
    pair_device_to_patient(1, 1)
    cur.execute("SELECT * FROM devices")
    print(cur.fetchall())
    unpair_device_from_patient(1, 1)
    cur.execute("SELECT * FROM devices")
    print(cur.fetchall())
    unpair_device_from_doctor(1, 1)
    cur.execute("SELECT * FROM devices")
    print(cur.fetchall())

    add_measurement(1.5, "loinc", 1, 1)

    add_doctor("hi", "t")
    delete_doctor(2)

    disconnect()
