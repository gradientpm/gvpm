import optparse
import subprocess
import sys
import os
import glob
import stat

class TechniqueOAR:
    def __init__(self, name):
        self.name = name
        self.commandIgrida = ""
        
    def configure(self, proc, output, input, dump):
        """Put in the commandIgrida field the parameters for Mitsuba"""
        inputFilename = input + "_" + self.name + ".xml"
        if(not os.path.exists(inputFilename)):
            raise Exception("Impossible to find "+ inputFilename)
            
        self.commandIgrida = ""
        self.commandIgrida += "-p " + str(proc)
        self.commandIgrida += " -o " + output + os.path.sep + self.name
        
        if(dump != ""):
            self.commandIgrida += " -r "+dump
        
        self.commandIgrida += " " + inputFilename
    
    def writeMtsLines(self, f):
        # === Write all values for mitsuba run
        f.write("export OMP_NUM_THREADS=1\n")
        f.write("$EXECUTABLE "+self.commandIgrida + "\n")
        
    def writeOutputLines(self, f, output):
        f.write("#OAR -E " + str(output + os.path.sep + self.name + ".err\n"))
        f.write("#OAR -O "+ str(output + os.path.sep + self.name + ".out\n"))
    
    

def launch(command):
    print(("[DEBUG] Launch: "+" ".join(command))) 
    process = subprocess.Popen(command,shell=False,stdout=subprocess.PIPE)
    return process.communicate()[0]

if __name__=="__main__":
    # === Read args
    parser = optparse.OptionParser()
    parser.add_option("-m", "--mitsuba", help="the mitsuba .sh")
    parser.add_option('-t','--technique', help='technique name', default=[], action="append")
    parser.add_option('-s','--time', help='time of running', default=None)
    parser.add_option('-i','--input', help='input scene name (%path_scene%_%tech%.xml)')
    parser.add_option('-o','--output', help='output directory')
    parser.add_option('-d','--dump', help='Force dum the image each seconds', default="")
    parser.add_option('-p','--proc', help='Force machine igrida', default=None)
    parser.add_option('-b','--bash', help='Write bash file command for later running', default=None)
    parser.add_option('-j','--jobs', help='nb thread per jobs', default=12)
    parser.add_option('-A','--automatic', help='replace -t usage by finding all files', default=False, action="store_true")
    (options, args) = parser.parse_args()
    
    # === Error handling
    if(options.input == None):
        print("\nError: Need input values\n")
        parser.print_help()
        sys.exit(1)
    if(options.output == None):
        print("\nError: Need output values\n")
        parser.print_help()
        sys.exit(1)
    if(options.time == None):
        print("\nError: Need to specif time\n")
        parser.print_help()
        sys.exit(1)
        
    # === Create output directory
    if(not os.path.exists(options.output)):
        os.makedirs(options.output)
        
    # === Create each techniques ...
    print("Create techniques ... ")
    techniques = []
    if(options.automatic):
        print(" === Automatic finding ...")
        files = glob.glob(options.input+"*.xml")
        for fileXML in files:
            filename = os.path.basename(fileXML)
            filenameRoot = os.path.basename(options.input)
            tech = filename[len(filenameRoot)+1:-4]
            print("   * Find: %s" % tech)
            techniques.append(TechniqueOAR(tech))
    else:   
        for tech in options.technique:
            techniques.append(TechniqueOAR(tech))
    
    bashFile = None
    if(options.bash):
        bashFile = open(options.bash, "w")
        bashFile.write("#!/bin/sh\n")
    # === Launch oar scheduling
    print("Scheduling OAR")
    for tech in techniques:
        # === Configure the Tech Object
        tech.configure(options.jobs, options.output, options.input, options.dump)
        
        # === Create the fileArgs
        fileArgsname = options.output + os.path.sep + "args" + tech.name + ".sh"
        fileArgs = open(fileArgsname, "w")
        
        # === Write OAR stuff
        fileArgs.write("#!/bin/sh\n")
        fileArgs.write("#OAR -l /nodes=1/core="+str(options.jobs)+",walltime="+options.time+"\n")
        tech.writeOutputLines(fileArgs,options.output)
        if(options.proc):
            fileArgs.write("#OAR -p cluster=\'" + options.proc + "\'\n")
        
        # === Write Executable value and MTS call
        fileArgs.write("EXECUTABLE="+options.mitsuba+"\n")
        dirnameMTS=os.path.dirname(options.mitsuba)
        fileArgs.write("export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:"+dirnameMTS+"\n") #TODO: Make it auto
        tech.writeMtsLines(fileArgs)
        
        # === Close and change writes
        fileArgs.close()
        st = os.stat(fileArgsname)
        os.chmod(fileArgsname, st.st_mode | stat.S_IEXEC)
        
        # === And write the args for calling OAR
        outArgs = ["oarsub", "-S", fileArgsname]
        if(options.bash):
            bashFile.write(" ".join(outArgs)+"\n")
        else:
            print(launch(outArgs))
