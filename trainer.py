import json
import sys
import subprocess
import os
import argparse
from kafka import KafkaConsumer, KafkaProducer
from common import Common

TRAIN_ROOT = os.path.abspath("../neural")
TRAIN_PATH = "../neural/run_train.sh"

parser = argparse.ArgumentParser()
parser.add_argument("name", help="Name of trainer.")
parser.add_argument("topic", help="Name of topic to consume from.")

cmd_args = parser.parse_args()

common = Common("Trainer_%s" % cmd_args.name)
common.load()

consumer = KafkaConsumer(
        cmd_args.topic,
        group_id="trainers", # Consumer group.
        enable_auto_commit=False, # Don't commit unless we successfully process request.
        auto_offset_reset="earliest",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")))

producer = KafkaProducer(
        value_serializer=lambda m: json.dumps(m).encode("utf-8"))

common.log("Trainer standing up.")

for message in consumer:
    # Decode request.
    name = message.key.decode("utf-8")

    # -
    # Source arguments
    # -
    args = message.value["args"] # Extra arguments to the training program.
    style = message.value["style"] # Name of style image to train with.
    starting_checkpoint = message.value["starting_checkpoint"] # Name of model to start training with.

    iterations_per_cycle = message.value["iterations_per_cycle"] # Number of iterations per cycle to run training with for this job.

    cycles_remaining = int(message.value["cycles_remaining"]) # Number of training cycles left.
    cycles_completed = int(message.value["cycles_completed"]) # Number of completed training cycles.

    base_learning_rate = float(message.value["base_learning_rate"]) # Learning rate.
    learning_decay = float(message.value["learning_decay"]) # Percentage to multiply learning rate by every learning_period cycles.
    learning_period = int(message.value["learning_period"]) # Number of cycles before reducing the learning rate.

    # -
    # Derived arguments
    # -
    has_starting_checkpoint = starting_checkpoint is not None and len(starting_checkpoint) > 0

    checkpoint_name = "%s_%d.t7" % (name, cycles_completed + 1)

    learning_rate = base_learning_rate*(learning_decay**(cycles_completed/learning_period))

    data_path = os.path.expanduser("~/flock/dataset")
    style_path = common.getpath("style", style)
    out_path = common.getpath("checkpoint", checkpoint_name)

    params = "-data %s -style_image %s -num_iterations %d -learning_rate %f -out %s %s" % (data_path, style_path, iterations_per_cycle, learning_rate, out_path, args)

    if has_starting_checkpoint:
        params = "%s -starting_checkpoint %s" % (params, common.getpath("checkpoint", starting_checkpoint))

    common.log("Received request (offset %d) named %s with style: %s, args: %s" % (message.offset, name, style, args))
            

    # Pull down assets.
    common.download("style", style)

    if has_starting_checkpoint:
        common.download("checkpoint", starting_checkpoint)
    
    # Run the training program.
    run_command = "/usr/bin/screen /usr/bin/sh %s %s" % (TRAIN_PATH, params)
    common.log("Executing command %s" % run_command)
    process = subprocess.Popen(run_command, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, universal_newlines=True, cwd=TRAIN_ROOT)
    process.wait()
    for line in process.stdout.readlines():
        common.log("Training program output: %s" % line)
    common.log("Return code: %d" % process.returncode)

    # Upload the completed checkpoint.
    common.upload("checkpoint", checkpoint_name)

    # Post a successor to this job, if we still have cycles remaining.
    # Otherwise, we're done! Hooray.
    if cycles_remaining > 1:
        next_task = message.value
        next_task["cycles_remaining"] = cycles_remaining-1
        next_task["cycles_completed"] = cycles_completed+1
        next_task["starting_checkpoint"] = checkpoint_name

        producer.send(cmd_args.topic, key=name.encode("utf-8"), value=next_task)

    # Commit that this message was processed for our consumer group.
    consumer.commit()
