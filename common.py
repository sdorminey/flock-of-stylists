import os
import requests
import time
from kazoo.client import KazooClient
from kafka import KafkaProducer

ZK_ENDPOINT = "127.0.0.1:2181"
DATA_FOLDER = "/srv/flock/data"

class Common:
    def __init__(self, identity):
        self.identity = identity
        self.producer = KafkaProducer()

    def load(self):
        self.zk = KazooClient(hosts=ZK_ENDPOINT)
        self.zk.start()

        self.fs_addr = self.zk.get("/flock/fileserver")[0].decode("utf-8")

    def log(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        line = "[%s] %s %s" % (self.identity, timestamp, message)
        self.producer.send("log", line.encode("utf-8"))
        print(line)

    def upload(self, category, path):
        filename = os.path.basename(path)
        with open(path, "rb") as f:
            requests.post(
                    "http://%s/%s/%s" % (self.fs_addr, category, filename),
                    data = f)

    def download(self, category, filename):
        path = os.path.join(DATA_FOLDER, self.identity, category, filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        if os.path.exists(path):
            self.log("Skipped downloading %s because we already have it." % path)
            return
        else:
            self.log("Downloading %s" % path)

        r = requests.get("http://%s/%s/%s" % (self.fs_addr, category, filename), stream=True)
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=4096):
                f.write(chunk)
