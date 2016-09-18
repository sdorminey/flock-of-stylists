from kafka import KafkaProducer
import json
import argparse
import os
from common import Common

common = Common("client")
common.load()

parser = argparse.ArgumentParser()
parser.add_argument("name", help="Name for the task to submit.")
parser.add_argument("args", help="Arguments to use for training.")
parser.add_argument("style", help="File name of style.")
parser.add_argument("iters", type=int, default=10, help="Iterations per cycle.")
parser.add_argument("cycles", type=int, default=10, help="Number of cycles to train for.")
parser.add_argument("learning_rate", type=float, default=10e-3, help="Initial learning rate.")
parser.add_argument("learning_decay", type=float, default=0.8, help="Discount factor for learning rate by period.")
parser.add_argument("learning_period", type=int, default=2, help="Number of cycles between learning rate discounts.")

args = parser.parse_args()

producer = KafkaProducer(
        value_serializer=lambda m: json.dumps(m).encode("utf-8"))

print ("Ready.")

style_path = os.path.abspath(args.style)
task =  {
            "args": args.args,
            "style": os.path.basename(style_path),
            "starting_checkpoint": "",
            "iterations_per_cycle": args.iters,
            "cycles_remaining": args.cycles,
            "cycles_completed": 0,
            "base_learning_rate": args.learning_rate,
            "learning_decay": args.learning_decay,
            "learning_period": args.learning_period
        }

common.log("Uploading %s" % style_path)

common.upload("style", style_path)
common.log("Upload complete; submitting job named %s" % args.name)

producer.send(common.get_topic(), key=args.name.encode("utf-8"), value=task)
common.log("Job submitted")
