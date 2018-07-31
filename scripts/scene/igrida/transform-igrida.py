"""
This script transform a given MTS 4.X files into a clay scene
"""
import os, sys, optparse
import xml.etree.ElementTree as ET

def transform_igrida(inpt, out):
    tree = ET.parse(inpt)
    sceneRoot = tree.getroot()
    
    # === Remove this balise ... 
    removeName = ["width", "height"]
    
    #<integer name="width" value="$width"/>
    #<integer name="height" value="$height"/>
    #<integer name="cropOffsetX" value="$cropX" />
    #<integer name="cropOffsetY" value="$cropY" />
    #<integer name="cropWidth" value="$cropWidth" />
    #<integer name="cropHeight" value="$cropHeight" />
    
    igridaName = [("width","$width"),
                  ("height","$height"),
                  ("cropOffsetX","$cropX"),
                  ("cropOffsetY","$cropY"),
                  ("cropWidth","$cropWidth"),
                  ("cropHeight","$cropHeight"),]
    # === Find all sensor
    for sensorNode in sceneRoot.iter("sensor"):
        filmNode = sensorNode.find('film')
        print(filmNode)
        if(filmNode):
            # === Clean all files
            removeNode = []
            for childFilm in filmNode:
                if("name" in childFilm.attrib):
                    name = childFilm.attrib["name"]
                    if(name in removeName):
                        print("Remove: "+name)
                        removeNode.append(childFilm)
            for r in removeNode:
                filmNode.remove(r)
            # === Add igrida flags
            for (n,v) in igridaName:
                 reflectanceNode = ET.SubElement(filmNode,'integer', 
                                                 {"name":n,
                                                  "value":v})
    tree.write(out)
    
if __name__=="__main__":
    parser = optparse.OptionParser()
    parser.add_option('-i','--input', help='input file')
    parser.add_option('-o','--output', help='output file')
    (opts, args) = parser.parse_args()
    
    if not(opts.input and opts.output):
        parser.error("Need input/output values")
    
    if not(os.path.exists(opts.input)):
        parser.error("Unable to find: "+str(opts.input))
    
    transform_igrida(opts.input, opts.output)