import argparse
import os
from common import Common

parser = argparse.ArgumentParser()
parser.add_argument("mode", help="upload|download")
parser.add_argument("category", help="Asset category.")
parser.add_argument("filename", help="File name of asset.")
parser.add_argument("--user", default="client", help="Name of user.")

args = parser.parse_args()

common = Common(args.user)
common.load()

print ("Ready. Mode %s." % args.mode)

if args.mode == "download":
    common.log("Downloading %s %s" % (args.category, args.filename))
    common.download(args.category, args.filename)
    common.log("Download compleat [sic].")

if args.mode == "upload":
    common.log("Uploading %s %s" % (args.category, args.filename))
    common.upload(args.category, args.filename)
    common.log("Upload compleat [sic].")
