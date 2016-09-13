from kafka import KafkaConsumer
import json
import sys
from common import Common

if len(sys.argv) < 2:
    print("Usage: trainer.py <Identity>")
    sys.exit(0)

common = Common("Trainer_%s" % sys.argv[1])
common.load()

consumer = KafkaConsumer(
        "training-2", # Topic.
        group_id="trainers", # Consumer group.
        enable_auto_commit=False, # Don't commit unless we successfully process request.
        value_deserializer=lambda m: json.loads(m.decode("utf-8")))

common.log("Trainer standing up.")

for message in consumer:
    # Decode request.
    name = message.key.decode("utf-8")
    style = message.value["style"]
    args = message.value["args"]

    common.log("Received request (offset %d) named %s with style: %s, args: %s"
            % (message.offset, name, style, args))

    common.download("style", style)

    # Pull the asset if we have it.
    #consumer.commit()
