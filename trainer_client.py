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

style_path = os.path.abspath(args.style)
task = {"args": args.args, "style": os.path.basename(style_path)}

common.log("Uploading %s" % style_path)

common.upload("style", style_path)
common.log("Upload complete; submitting job named %s" % args.name)

producer.send("training-2", key=args.name.encode("utf-8"), value=task)
common.log("Job submitted")
