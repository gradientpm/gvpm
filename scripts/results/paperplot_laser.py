import optparse
import glob
import os
import csv_utils
import matplotlib.pyplot as plt
from pylab import *
import numpy as np
import matplotlib.transforms as transforms
import showResults
from matplotlib import rc, font_manager
from decimal import *

class AlgorithmPlot:
    def __init__(self, name, gradFile, primalFile,
                 style, color, inFocus = True):
        self.name = name
        self.gradFile = gradFile
        self.primalFile = primalFile
        self.curveStyle = style
        self.color = color
        self.inFocus = inFocus

        self.values = {}
        self.gradValues = {}
if __name__=="__main__":
    parser = optparse.OptionParser()
    parser.add_option('-o','--output', help="output pdf name", default="")
    parser.add_option('-t','--timelabel', help='Show time label', default=False, action="store_true")
    (opts, args) = parser.parse_args()
    
    #############################
    ### SETTINGS
    #############################
    isLogLog = False
    ABSPath = "/home/muliana/projects/gradient/volumegradient_pm_paper/figures/svg/csv/pack/" #"/home/beltegeuse/projects/GradientPM/volumegradient_pm_paper/figures/svg/csv/pack/"
    errorName = "relMSE"
    algorithms = [ AlgorithmPlot("VPM",
                                 "G-VPM_L1_areaMIS_null",
                                 "VPM",
                                 "-",
                                 (116,250,110)), # Green
                   AlgorithmPlot("BRE",
                                 "G-BRE_L1_areaMIS_null",
                                 "BRE",
                                 "-", (188,61,222)), # Purple
                   AlgorithmPlot("Beams",
                                 "G-Beam_L1_areaMIS_null_3D",
                                 "Beam_3D",
                                 "-",
                                 (69,147,250)), # Blue
                   AlgorithmPlot("Planes",
                                 "G-Plane_L1_areaMIS",
                                 "Plane",
                                 "-",
                                 (245,122,80)) # Red
                  ]
    G = [(0,0.0),(225,0.255),(45,0.45),(675,0.675),(9,0.9)]
    maxLenghtData = 0

    # Construct techniques names
    for g,gFloat in G:
        dirG = ABSPath+"g_0_"+str(g)

        requestedTech = []
        for alg in algorithms:
            requestedTech.append(alg.gradFile)
            requestedTech.append(alg.primalFile)

        # Read all the requested techniques
        # And copy the data values
        techniques = showResults.readAllTechniques(requestedTech, dirG, 5, False,  basey='_'+errorName+'.csv')
        for alg in algorithms:
            # Search the association between name and requested names
            # --- Gradients
            currentTech = None
            for tech in techniques:
                if tech.name == alg.gradFile:
                    currentTech = tech
            (times, values) = (currentTech.x, currentTech.y)
            alg.gradValues[ gFloat ] = (times[-1],values[-1])

            # --- Normal
            currentTech = None
            for tech in techniques:
                if tech.name == alg.primalFile:
                    currentTech = tech
            (times, values) = (currentTech.x, currentTech.y)
            alg.values[ gFloat ] = (times[-1],values[-1])

    # Compute the curves:
    extractedData = {}
    for alg in algorithms:
        v = []
        for g,gFloat in G:
            v += [alg.values[gFloat][1] / alg.gradValues[gFloat][1]]
        extractedData[alg.name] = ([gFloatCurr for g,gFloatCurr in G], v)

    # Change the font option
    sizeOfFont = 7.97*3
    fontProperties = {'family':'serif','serif':['Nimbus Roman'],
                      'weight' : 'normal', 'size' : sizeOfFont}
    rc('text', usetex=True)
    rc('font',**fontProperties)
    
    fig = plt.figure(figsize=(4,2), dpi=120) #,dpi=80
    ax = fig.add_subplot(1,1,1)

    # # Compute the min and max x/y values
    # maxyvalue = -10000
    # minyvalue = 10000
    # minxvalue = 10000
    # maxyvalueFocus = -10000
    # for alg in algorithms:
    #     # Take care only in focus techniques for the window clamping
    #     data = extractedData[ alg.name ]
    #     if alg.inFocus:
    #         maxyvalue = max( maxyvalue, max(data[1]) )
    #         maxyvalueFocus = max(maxyvalueFocus, max(data[1]) )
    #     else:
    #         maxyvalue = max( maxyvalue, max(data[1]) / 10.0 )
    #     minyvalue = min( minyvalue, min(data[1]) )
    #     minxvalue = min( minxvalue, min(data[0]) )
    # print("MIIN!!!MAX!!!",minyvalue,(minyvalue+maxyvalueFocus)*0.05,maxyvalue)
    # minyvalue = 0.0001
    # maxyvalue = maxyvalueFocus = 0.01

    yAxis = [1, 5, 10, 20] # GVPM values

    # For all the algorithm
    # Plot them
    for alg in algorithms:
        data = extractedData[ alg.name ]
        rC,gC,bC = alg.color
        C = (rC/255.0,gC/255.0,bC/255.0)
        
        lineWidthCurve = 10/3
        zorderCurve = 3

        line, = plt.plot(data[0], data[1] ,
                         label=alg.name, markevery=10, markersize=16,
                         linewidth=lineWidthCurve, color=C, linestyle=alg.curveStyle)
        line.set_zorder(zorderCurve)
    
        print("isLogLog = " + str(isLogLog))     
        if isLogLog:
            ax.set_xlim(minxvalue,1800)
            lowerLimit = 0.1
            ax.set_ylim(0,maxyvalue+0.01)
            #ax.set_yscale('log')
            #ax.set_xscale('log')
            ax.loglog()
            ax.set_xticks([gFloatCurr for g,gFloatCurr in G]) # 1200

            # If a time label is requested
            if(opts.timelabel):
                ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
            ax.xaxis.set_tick_params(labelsize=sizeOfFont)
            ax.set_yticks(yAxis) # 
            ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
            ax.yaxis.set_tick_params(labelsize=sizeOfFont)
            ax.grid(color='black', linestyle='--', linewidth=2/3)
        else:
            print("No log is not implemented yet")
            ax.set_xlim(0.0,0.9)
            lowerLimit = 0
            if errorName == "rmse_time":
                lowerLimit = 0.02
            else:
                lowerLimit = 0.1
            ax.set_ylim(0,25)
            ax.set_yticks([1,10,20])
            ax.set_xticks([gFloatCurr for g,gFloatCurr in G]) # 1200

            # If a time label is requested
            #if(opts.timelabel):
            #    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
            #ax.xaxis.set_tick_params(labelsize=sizeOfFont)
            #ax.set_yticks([minyvalue,(minyvalue+maxyvalueFocus)*0.5,maxyvalue])
            #ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
            #ax.yaxis.set_tick_params(labelsize=sizeOfFont)
            ax.grid(color='black', linestyle='--', linewidth=2/3)
             
    
    # --- Setup order and style
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # --- Setup tick precision
    #yy, locs = plt.yticks()
    #ll = [ "{:.1E}".format(Decimal(str(a))) for a in yy]
    #plt.yticks(yy, ll)
    
    # --- Setup tick space 
    for tick in ax.get_xaxis().get_major_ticks():
        tick.set_pad(8./3)
        #tick.set_fontproperties(ticks_font)
    for tick in ax.get_yaxis().get_major_ticks():
        tick.set_pad(16./3)
        #tick.set_fontproperties(ticks_font)
    
    # --- Remove minor tick up and right
    ax.tick_params(axis='x',which='minor',top='off')
    ax.tick_params(axis='y',which='minor',right='off')
    
    #if errorName == "rmse_time":
    #    plt.ylabel('RMSE',fontsize=40)
    #else:
    #  	plt.ylabel('NSD',fontsize=40)  
    #plt.xlabel('Time (sec.)',fontsize=40)  
    
    #if(isLogLog):
    #    plt.axes().set_aspect('equal')
        
    #legend = [alg.name for alg in algorithms]
    #plt.legend(legend, 'upper center', shadow=True, loc = 'upper right', bbox_to_anchor = (0.23, 0.23) )
    
    #plt.grid(True,lw=1,which='both')
    #plt.subplots_adjust(left=0.1, right=1, bottom=0.1, top=1.0)
    plt.savefig( opts.output, format='pdf' )
    #plt.savefig( dirName + os.path.sep + "plot_" + errorName + ".png", format='png' )
    #plt.show()
