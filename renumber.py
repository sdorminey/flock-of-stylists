import os
import argparse
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("path", help="Path with files to renumber.")
parser.add_argument("fmt", help="Format (e.g. %04d.jpg)")

args = parser.parse_args()

expanded_path = os.path.realpath(os.path.expanduser(args.path))

files = [f for f in os.listdir(expanded_path) if os.path.isfile(os.path.join(expanded_path, f))]
files.sort()

for index, f in enumerate(files):
    src = os.path.join(expanded_path, f)
    dst = os.path.join(expanded_path, args.fmt % index)
    print("%s -> %s" % (src, dst))
    shutil.move(src, dst)
