from kafka import KafkaProducer
import json
import argparse
import os
from common import Common

common = Common("client")
common.load()

parser = argparse.ArgumentParser()
parser.add_argument("topic", help="Name for the topic to submit to.")
parser.add_argument("name", help="Name for the task to submit.")
parser.add_argument("style", help="File name of style.")
parser.add_argument("--args", default='-backend cudnn -batch_size 1 -model starling', help="Arguments to use for training.")
parser.add_argument("--iters", type=int, default=250, help="Iterations per cycle.")
parser.add_argument("--cycles", type=int, default=200, help="Number of cycles to train for.")
parser.add_argument("--learning_rate", type=float, default=4e-2, help="Initial learning rate.")
parser.add_argument("--learning_decay", type=float, default=0.8, help="Discount factor for learning rate by period.")
parser.add_argument("--learning_period", type=int, default=25, help="Number of cycles between learning rate discounts.")

args = parser.parse_args()

producer = KafkaProducer(
        value_serializer=lambda m: json.dumps(m).encode("utf-8"))

print ("Ready.")

task =  {
            "args": args.args,
            "style": args.style,
            "starting_checkpoint": "",
            "iterations_per_cycle": args.iters,
            "cycles_remaining": args.cycles,
            "cycles_completed": 0,
            "base_learning_rate": args.learning_rate,
            "learning_decay": args.learning_decay,
            "learning_period": args.learning_period
        }

common.log("Uploading %s" % args.style)

common.upload("style", args.style)
common.log("Upload complete; submitting job named %s" % args.name)

producer.send(args.topic, key=args.name.encode("utf-8"), value=task)
common.log("Job submitted")
