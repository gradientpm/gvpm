import optparse
import subprocess

def getAllProc(user, type):
    command = "oarstat -u " + user
    formatCommand = command.split()
    process = subprocess.Popen(formatCommand,shell=False,stdout=subprocess.PIPE)
    programOutput = process.communicate()[0]
    programOutputLines = programOutput.split("\n")[2:-1]
    ids = [line.split()[0] for line in programOutputLines]
    return ids

def deleteProc(id):
    command = "oardel " + id
    formatCommand = command.split()
    process = subprocess.Popen(formatCommand,shell=False,stdout=subprocess.PIPE)
    programOutput = process.communicate()[0]
    return programOutput

ids = getAllProc("agruson", "besteffort")
for i in range(len(ids)):
    id = ids[i]
    print(deleteProc(id))
    
