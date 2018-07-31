import optparse
import os
import glob
import sys
import shutil
import demjson

files = ["rmse.js", "relMSE.js", "logrmse.js", "logrelMSE.js", "time.js"]
colors = ["#DAF7A6", "#FFC300", "#FF5733", "#C70039", "#900C3F", "#581845", "#B84B4B", "#BAB14D", "#568A73",
          "#565E8A", "#85568A", "#556270", "#4ECDC4", "#C7F464", "#FF6B6B", "#C44D58"]

HTMLCode = """<html xmlns="http://www.w3.org/1999/xhtml">

<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>Comparison</title>
<meta http-equiv="Content-Language" content="English">

<script type="text/javascript" src="./js/jquery.min.js"></script>
<script type="text/javascript" src="./js/image-compare.js"></script><script type="text/javascript" src="./js/Chart.min.js"></script><script type="text/javascript" src="./js/Chart.min.js"></script>
</style>
</head><body>

<br>
<h2>relMSE</h2>
<button onclick="relMSEHide()">Hide all curves</button><button onclick="relMSEShow()">Show all curves</button><div style="width:960px;height:540px;background-color:#d8d8d8"><canvas id="relMSE"></canvas></div>
<script src="relMSE.js" type="text/javascript" language="javascript"></script><p></p>
<button onclick="logrelMSEHide()">Hide all curves</button><button onclick="logrelMSEShow()">Show all curves</button><div style="width:960px;height:540px;background-color:#d8d8d8"><canvas id="logrelMSE"></canvas></div>
<script src="logrelMSE.js" type="text/javascript" language="javascript"></script><p></p><h2>RMSE</h2>
<button onclick="rmseHide()">Hide all curves</button><button onclick="rmseShow()">Show all curves</button><div style="width:960px;height:540px;background-color:#d8d8d8"><canvas id="rmse"></canvas></div>
<script src="rmse.js" type="text/javascript" language="javascript"></script><p></p>
<button onclick="logrmseHide()">Hide all curves</button><button onclick="logrmseShow()">Show all curves</button><div style="width:960px;height:540px;background-color:#d8d8d8"><canvas id="logrmse"></canvas></div>
<script src="logrmse.js" type="text/javascript" language="javascript"></script><p></p><h2>Rendering time</h2><p>Number of second for each iterations</p>
<button onclick="timeHide()">Hide all curves</button><button onclick="timeShow()">Show all curves</button><div style="width:960px;height:540px;background-color:#d8d8d8"><canvas id="time"></canvas></div>
<script src="time.js" type="text/javascript" language="javascript"></script><p></p>
</body>
"""

def foundDataSeq(fileArray):
    iData = 0
    while not("datasets:" in fileArray[iData]):
        iData+=1

    iOptions = iData + 1
    while not("}]}]}" in fileArray[iOptions]):
        iOptions+=1

    return (iData+1, iOptions)

def renameTechniques(fileArray, iS, iE, newS):
    for i in range(iS, iE):
        fileArray[i] = fileArray[i].replace('label: "', 'label: "'+newS)

parser = optparse.OptionParser()
parser.add_option('-i','--input', help='input dir', default="")
parser.add_option('-s','--scenes', help='scene name', default=[], action="append")
parser.add_option('-o','--output', help='output html dir', default="")
parser.add_option('-H','--html', help='output html dir', default=[], action="append")
parser.add_option('-F','--filter', help='filter name', default=[], action="append")
parser.add_option('-C','--color', help='re-color the curves', default=False, action="store_true")

(opts, args) = parser.parse_args()

for s in opts.scenes:
    orgPath = [opts.input + os.path.sep + s + "_scene" + os.path.sep + "html" + name + os.path.sep for name in opts.html]
    destPath = opts.input + os.path.sep + s + "_scene" + os.path.sep + "html" + opts.output + os.path.sep

    if(not os.path.exists(destPath)):
        os.mkdir(destPath)

    # Create the main html
    fHTML = open(destPath + "index.html","w")
    fHTML.write(HTMLCode)
    fHTML.close()

    # Copy all JS
    if(not os.path.exists(destPath + "js")):
        shutil.copytree(orgPath[0] + "js", destPath + "js")

    for filenameJS in files:
        fJSFile = open(orgPath[0] + filenameJS, "r").readlines()
        iS, iE = foundDataSeq(fJSFile)
        renameTechniques(fJSFile, iS, iE, opts.html[0])
        for iHTML in range(1, len(opts.html)):
            otherFile = open(orgPath[iHTML] + filenameJS, "r").readlines()
            iSOther, iEOther = foundDataSeq(otherFile)
            otherFile[iEOther] = otherFile[iEOther].replace("}]}]}", "}]},")
            renameTechniques(otherFile, iSOther, iEOther, opts.html[iHTML])
            fJSFile = fJSFile[:iS] + otherFile[iSOther:iEOther+1] + fJSFile[iS:]

        # Filtering code
        iS, iE = foundDataSeq(fJSFile)
        # add "[" and remove "}]"
        datasetJSON = demjson.decode("["+(''.join(fJSFile[iS:iE+1]))[:-2])

        if opts.filter:
            newDatasetJSON = []
            for el in datasetJSON:
                for f in opts.filter:
                    if f in (el["label"]):
                        newDatasetJSON += [el]
                        print(el["label"])
                        break # Quit
            datasetJSON = newDatasetJSON

        if opts.color:
            id = 0
            for el in datasetJSON:
                el["borderColor"] = colors[id]
                el["backgroundColor"] = colors[id]
                id += 1

        outputData = demjson.encode(datasetJSON)
        outputData = outputData[1:]+"} "
        fJSFile[iS:iE+1] = [outputData]


        # Out
        fJSOut = open(destPath + filenameJS, "w")
        for line in fJSFile:
            fJSOut.write(line)
        fJSOut.close()


