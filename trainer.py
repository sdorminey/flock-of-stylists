from kafka import KafkaConsumer
import json
from kazoo.client import KazooClient

# Initialize ZooKeeper client and Kafka consumer.
zk = KazooClient(hosts="127.0.0.1:2181")
zk.start()

consumer = KafkaConsumer(
        "training", # Topic.
        group_id="trainers", # Consumer group.
        enable_auto_commit=False, # Don't commit unless we successfully process request.
        value_deserializer=lambda m: json.loads(m.decode("utf-8")))

fileserver_endpoint = zk.get("/flock/fileserver")[0].decode("utf-8")

print ("Fs endpoint: %s" % fileserver_endpoint)

for message in consumer:
    name = message.key.decode("utf-8")
    style = message.value["style"]
    args = message.value["args"]
    print ("Received request (offset %d) named %s with style: %s, args: %s"
            % (message.offset, name, style, args))
    #consumer.commit()
