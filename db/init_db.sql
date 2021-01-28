CREATE TABLE doctors(
    id SERIAL PRIMARY KEY,
	name VARCHAR(20) NOT NULL,
	surname VARCHAR(20) NOT NULL
);

CREATE TABLE patients(
	id SERIAL PRIMARY KEY,
	name VARCHAR(20) NOT NULL,
	surname VARCHAR(20) NOT NULL
);

CREATE TABLE devices(
	id SERIAL PRIMARY KEY,
	name VARCHAR(40) NOT NULL,
    loinc_num VARCHAR NOT NULL,
    mac VARCHAR(20) UNIQUE NOT NULL,
    taken BOOLEAN NOT NULL DEFAULT FALSE,
    doctor_id INT DEFAULT NULL,
    patient_id INT DEFAULT NULL,
    FOREIGN KEY(doctor_id) REFERENCES doctors(id) ON DELETE SET NULL,
    FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE SET NULL
);

CREATE TABLE measurements(
	id SERIAL PRIMARY KEY,
	val DECIMAL NOT NULL,
	device_id VARCHAR(20),
	patient_id INT,
	date TIMESTAMP,
	unit_id INT,
    FOREIGN KEY(device_id) REFERENCES devices(mac) ON DELETE SET NULL,
    FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE SET NULL
);

CREATE TABLE loinc_data(
    id SERIAL PRIMARY KEY,
    time VARCHAR(50),
    system VARCHAR(50),
    scale_typ VARCHAR(50),
    property VARCHAR(100),
    method_typ VARCHAR(50),
    loinc_num VARCHAR(10) NOT NULL,
    component VARCHAR(100),
    unit VARCHAR(30)
)

