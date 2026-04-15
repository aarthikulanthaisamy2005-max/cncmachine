import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point

# InfluxDB config
url = "http://localhost:8086"
token = "bo-p211yR3djJCASUqCgu9SO1Bv6TV1tKr121AiFJFQu74Ufwt5y0jX36ntlTZC-q_chfZZRGLm6yJgDzo0qDg=="
org = "my-org"
bucket = "machine_data"

client_db = InfluxDBClient(url=url, token=token, org=org)
write_api = client_db.write_api()

def on_message(client, userdata, message):
    value = float(message.payload.decode())

    print("Received:", value)

    point = Point("sensor") \
        .field("value", value)

    write_api.write(bucket=bucket, org=org, record=point)

    print("Saved to InfluxDB:", value)

client = mqtt.Client()
client.connect("localhost", 1883)

client.subscribe("sensor/value")
client.on_message = on_message

print("Waiting for data...")
client.loop_forever()