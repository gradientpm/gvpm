import xml.dom.minidom as dom
import optparse

def extractBalise(xmlSource, xmlSearch, values):
    if(xmlSource.nodeType != xmlSource.ELEMENT_NODE):
        return
    if(xmlSearch.nodeType != xmlSearch.ELEMENT_NODE):
        return
    
    # Test the matching between different element
    match = True
    match &= (xmlSource.tagName == xmlSearch.tagName)
    if(not match):
        return
    
    for k in xmlSearch._attrs.keys():
        v = xmlSearch._attrs[k].nodeValue

        match &= (k in xmlSource._attrs.keys())
        if(not match):
            return

        if(v[0] == "$"):
            #print("Found Keys :)")
            values[v[1:]] = xmlSource._attrs[k].nodeValue
        else:
            match &= (xmlSource._attrs[k].nodeValue == v)
     
    if(not match):
        return
    
    # In the case of corresponding candidate => continue to search
    for bSource in xmlSource.childNodes:
        for bSearch in xmlSearch.childNodes:
            extractBalise(bSource, bSearch, values)
    
def extractDict(sourceText, searchText):
    xmlSource = dom.parseString(sourceText)
    xmlSearch = dom.parseString(searchText)
    
    values = {}
    for bSource in xmlSource.childNodes:
        for bSearch in xmlSearch.childNodes:
                extractBalise(bSource, bSearch, values)
    return values

def extractXml(sourceText, searchText, template = None, output = None):
    inputFile = open(sourceText, 'r')
    searchFile = open(searchText, 'r')
    sourceText = inputFile.read()
    searchText = searchFile.read()
    
    dict = extractDict(sourceText, searchText)
    
    print('Keys founds ... ')
    for (k,v) in dict.items():
        print(" *",k,"=",v)
    print("nb Keys founds: "+str(len(dict)))
    if template:
        if not output:
            print("Need output args for template strategy")
            return
        
        templateFile = open(template, 'r')
        outputFile = open(output,'w')
        
        templateText = templateFile.read()
        for (k,v) in dict.items():
            templateText = templateText.replace('"'+"$"+k+'"', '"'+v+'"')
        print("Write ... ", output)
        outputFile.write(templateText)
    
if __name__=="__main__":
    parser = optparse.OptionParser()
    parser.add_option('-s','--search', help='search file')
    parser.add_option('-i','--input', help='input file (source)')
    parser.add_option('-t','--template', help='template file')
    parser.add_option('-o','--output', help='output file')
    
    (options, args) = parser.parse_args()
    
    inputFile = open(options.input, 'r')
    searchFile = open(options.search, 'r')
    
    sourceText = inputFile.read()
    searchText = searchFile.read()
    
    dict = extractDict(sourceText, searchText)
    
    print('Keys founds ... ')
    for (k,v) in dict.items():
        print(" *",k,"=",v)
        
    if(options.template):
        if(not options.output):
            print("Need --output args for template strategy")
            exit()
        templateFile = open(options.template, 'r')
        outputFile = open(options.output,'w')
        
        templateText = templateFile.read()
        for (k,v) in dict.items():
            templateText = templateText.replace("$"+k, v)
        print("Write ... ", options.output)
        outputFile.write(templateText)
        