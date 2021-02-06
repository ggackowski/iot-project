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
    loinc_number VARCHAR NOT NULL,
    uuid VARCHAR(40) UNIQUE NOT NULL,
    unit VARCHAR(10),
    minimum_indication INT,
    maximum_indication INT
);

CREATE TABLE measurements(
	id SERIAL PRIMARY KEY,
	val DECIMAL NOT NULL,
	device_id VARCHAR(40),
	patient_id INT,
	date TIMESTAMP,
    FOREIGN KEY(device_id) REFERENCES devices(uuid) ON DELETE SET NULL,
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

