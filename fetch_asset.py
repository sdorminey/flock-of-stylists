import argparse
import os
from common import Common

common = Common("client")
common.load()

parser = argparse.ArgumentParser()
parser.add_argument("category", help="Asset category.")
parser.add_argument("filename", help="File name of asset.")

args = parser.parse_args()

print ("Ready.")

common.log("Downloading %s %s" % (args.category, args.filename))

common.download(args.category, args.filename)

common.log("Download compleat [sic].")
