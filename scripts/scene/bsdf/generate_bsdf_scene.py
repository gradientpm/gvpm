import os, sys, optparse
import xml.etree.ElementTree as ET

def findBSDF(sceneRoot):
    for bsdf in sceneRoot.iter("bsdf"):
        if(bsdf.attrib["id"] == "mymat-material"):
            return bsdf
    
    print("ERROR: BSDF is not found, QUIT")
    sys.exit(1)
    return 0

def replaceBSDF(ori, new):
    # === Transfer the type
    ori.attrib["type"] = new.attrib["type"]
    
    # === Remove childs
    oriChilds = []
    for child in ori:
        oriChilds.append(child)
    
    for child in oriChilds:
        ori.remove(child)
        
    # === Add new childs
    for child in new:
        ori.insert(0, child)
    

def readConfigFile(configFile):
    tree = ET.parse(configFile)
    materialsRoot = tree.getroot()
    
    mats = {}
    
    for mat in materialsRoot.iter("Material"):
        mats[mat.attrib["name"]] = mat.find("bsdf")
    
    print("Loaded mats: ")
    for name, xml in mats.iteritems():
        print(name+" : "+ ET.tostring(xml, encoding='utf8', method='xml'))
    
    return mats
    

if __name__=="__main__":
    parser = optparse.OptionParser()
    parser.add_option('-i','--input', help='input XML scene file')
    parser.add_option('-c','--config', help='config material file')
    parser.add_option('-o','--output', help='output directory')
    parser.add_option('-n','--name', help='basename generated files')
    parser.add_option('-1','--num', help='use num for name (igrida)', action="store_true", default=False)
    
    (opts, args) = parser.parse_args()
    
    mats = readConfigFile(opts.config)
    
    tree = ET.parse(opts.input)
    sceneRoot = tree.getroot()
    
    bsdfRemplacement = findBSDF(sceneRoot)
    
    num = 0
    for name, xml in mats.iteritems():
        outputFile = opts.output + os.path.sep + opts.name + "_"
        if(opts.num):
            outputFile += str(num).zfill(5) + ".xml"
        else:
            outputFile += name + ".xml"
        replaceBSDF(bsdfRemplacement, xml)
        
        print("Write: "+outputFile)
        tree.write(outputFile)
        num += 1
    
    if(opts.num):
        # write the correspondance table
        f = open("./data/correspond.txt","w")
        num = 0
        for name, xml in mats.iteritems(): 
            f.write(str(num).zfill(5) + ":" + name + "\n")
            num += 1
        f.close()