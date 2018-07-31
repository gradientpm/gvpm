"""The aim of this script is to combine results
for all the scenes given"""

import optparse
import sys
import os
import shutil
import glob
SCENES = ["bathroom", "bookshelf", "bottle", "cbox",
          "pmbox", "kitchen", "veach-lamp"]

parser = optparse.OptionParser()

parser.add_option('-i','--input', help='input dir', default="")
parser.add_option('-o','--output', help='combined output name', default="")

# Hours,GPM,GPM_old -> resHours, GPM* => GPM_old (rename)
parser.add_option('-t','--technique', help='Technique input: Hours,GPM,GPM_old', default=[], action="append")

# Read input
(opts, args) = parser.parse_args()

if(opts.input == ""):
    print("Need to specify inputs")
    parser.print_help()
    sys.exit(1)

if(opts.output == ""):
    print("Need to specify output")
    parser.print_help()
    sys.exit(1)

#############
# Parse all the techniques
print(opts.technique)
techniques = []
for tech in opts.technique:
    info = tech.split(",")
    if len(info) > 3 or len(info) < 2:
        print("Bad technique name: "+tech)
        parser.print_help()
        sys.exit(1)
    if(len(info) == 2):
        # Copy name for renaming
        info = [info[0], info[1], info[1]]
    techniques.append(info)

print(techniques)

for scene in SCENES:
    sceneDir = opts.input + os.path.sep + scene + "_scene"
    newResDir = sceneDir + os.path.sep + "res" + opts.output

    # Create the directory

    if(os.path.exists(newResDir)):
        shutil.rmtree(newResDir)
    os.makedirs(newResDir)

    for tech in techniques:
        curDir = sceneDir + os.path.sep + "res" + tech[0]
        files = glob.glob(curDir + os.path.sep + tech[1] + "*")
        for f in files:
            newFname = f.replace(tech[1], tech[2])
            newFname = newFname.replace(curDir, newResDir)
            print(f, "=>", newFname)
            shutil.copyfile(f, newFname)
