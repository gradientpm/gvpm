statsMatches = [("diff","-  Percentage Diff. Vol Shift :  :"),
                ("me","-  Percentage ME Vol Shift    :"),
                #("nonvis","-  Percentage non visible Vol Shift :  :"),
                ("nullshift", "-  Percentage of null shift :  :")]

statsMatchesBeam = [("diff","-  Percentage Diff. Vol Shift :  :"),
                ("me","-  Percentage ME Vol Shift    :"),
                #("nonvis","-  Percentage non visible Vol Shift :  :"),
                ("nullshift", "Percentage of additional shift:  :")]



def readStats(name, matches):
    f = open(name, "r")
    lines = f.readlines()

    stats  = {}
    for s, p in matches:
        stats[s] = []

    for l in lines:
        for s, p in matches:
            if p in l:
                stats[s] += [float(l[l.rfind(":")+1:l.find("%")-1])]
    #print(stats)

    # Get the last match
    lastMatch = {}
    for s, p in matches:
        lastMatch[s] = stats[s][-1]
        #TODO: Check the number of entry
    return lastMatch

import numpy as np
import matplotlib.pyplot as plt

path = "/home/muliana/projects/gradient/FINAL/resJan23/"
scenes = ["kitchen_scene/resFINAL", "staircase_scene/resFINAL", "bathroom_scene/resFINAL", "bathroom_apr17_scene/resFINAL"]
techniques = [("G-VPM_L1_areaMIS_null.out",statsMatches, "G-VPM"),
              ("G-BRE_L1_areaMIS_null.out",statsMatches, "G-BRE"),
              ("G-Beam_L1_areaMIS_null_3D.out",statsMatchesBeam, "G-Beam")]

nullShifts = []
MEShifts = []
DiffuseShifts = []
name = []
N = 0
for s in scenes:
    for t,m,n in techniques:
        filename = path + s + "/" + t
        print(filename)
        stats = readStats(filename,m)
        print(stats)

        nullShifts += [stats["nullshift"]]
        other = (100 - stats["nullshift"]) / 100
        if(m == statsMatchesBeam):
            other = 1

        MEShifts += [stats["me"]*other]
        DiffuseShifts += [stats["diff"]*other]
        N += 1

        name += [n]

ind = np.arange(N)    # the x locations for the groups
width = 0.35       # the width of the bars: can also be len(x) sequence

nonNull = [MEShifts[i]+DiffuseShifts[i] for i in range(len(MEShifts))]

p1 = plt.bar(ind, DiffuseShifts, width)
p2 = plt.bar(ind, MEShifts, width, bottom=DiffuseShifts)
p3 = plt.bar(ind, nullShifts, width, bottom=nonNull)

#
plt.ylabel('Shifts')
plt.title('Shifts by rendering technique')
plt.xticks(ind, name)
#plt.yticks(np.arange(0, 81, 10))
plt.legend((p1[0], p2[0], p3[0]), ('Diffuse', 'ME', "NullShift"))
#
plt.show()

#print(readStats("/home/belteguse/projects/gradient/results/rawDataAcc/G-VPM_L2_areaMIS.out"))

