import optparse
import os

parser = optparse.OptionParser()
parser.add_option('-i','--input', help='input dir', default="")
parser.add_option('-s','--scenes', help='scene name', default=[], action="append")
parser.add_option('-o','--output', help='output name')

import glob

(opts, args) = parser.parse_args()

# Remove the dir sep if necessary
inputDir = opts.input
if(opts.input[-1] == os.path.sep):
    inputDir = inputDir[:-1]

files = []
for sc in opts.scenes:
    resPath = inputDir + os.path.sep + sc + "_scene" + os.path.sep + "res" + opts.output
    if(os.path.exists(resPath)):
        files += glob.glob(resPath + os.path.sep + "*")
    else:
        print("the path", resPath, "doesn't exist, do not pack it")

print("Files lists: ")
for f in files:
    print("  * ", f)

zipFile = inputDir + os.path.sep + opts.output + ".tar"
if(os.path.exists(zipFile)):
    print("Delete older file in", zipFile)
    os.remove(zipFile)

print("Zip into -> ", zipFile)
import tarfile
out = tarfile.open(zipFile, mode='w')

for f in files:
    newFileName = f.replace(inputDir + os.path.sep, "")
    out.add(f, arcname=newFileName)
    print(newFileName)

