from kafka import KafkaProducer
import json
import argparse
import os
from common import Common

common = Common("Client")
common.load()

parser = argparse.ArgumentParser()
parser.add_argument("name", help="Name for the task to submit.")
parser.add_argument("style", help="File name of style.")
parser.add_argument("args", help="Arguments to use for training.")
args = parser.parse_args()

producer = KafkaProducer(
        value_serializer=lambda m: json.dumps(m).encode("utf-8"))

print ("Ready.")

task = {"args": args.args, "style": args.style}

path = os.path.abspath(args.style)
common.log("Uploading %s" % path)

common.upload("style", path)
common.log("Upload complete; submitting job named %s" % args.name)

producer.send("training", key=args.name.encode("utf-8"), value=task)
common.log("Job submitted")
