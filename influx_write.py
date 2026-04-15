from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import time
import random

# 🔑 InfluxDB config
token = "bo-p211yR3djJCASUqCgu9SO1Bv6TV1tKr121AiFJFQu74Ufwt5y0jX36ntlTZC-q_chfZZRGLm6yJgDzo0qDg=="
org = "my-org"
bucket = "machine_data"
url = "http://localhost:8086"

client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

while True:
    # 🔥 Generate sensor data
    temperature = random.randint(20, 100)
    vibration = round(random.uniform(0.5, 5.0), 2)
    rpm = random.randint(500, 3000)

    # 🚨 Status logic
    if vibration < 2:
        status = "NORMAL"
    elif vibration < 4:
        status = "WARNING"
    else:
        status = "ANOMALY"

    # 📦 Create data point
    point = Point("cnc_machine") \
        .field("temperature", temperature) \
        .field("vibration", vibration) \
        .field("rpm", rpm) \
        .tag("status", status)

    # 📤 Write to InfluxDB
    write_api.write(bucket=bucket, org=org, record=point)

    print(f"Temp: {temperature} | Vib: {vibration} | RPM: {rpm} | Status: {status}")

    time.sleep(2)