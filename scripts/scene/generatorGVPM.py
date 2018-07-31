#######
# Global config
#######
# --- Path tracing techniques
rrDepthPaths = "5" # Not do RR 1 
timeMax = "3700" # 1h + 100 sec
samplesPT = "128"
samplesBDPT = "16"
samplesGBDPT = str(int(samplesBDPT) // 2)
samplesGPT = str(int(samplesPT) // 2)
samplesVRL = "1"
multIterationBDPT = "5" # Doesn't work if the iteration not matches
cameraSphere = "1.0"

##############################
# Functions
##############################
def xmlEntry(type, name, value):
    return (type,{"name":name,"value":value})

def xmlIntAttrs(type, attrs):
    return ("integrator",{"type":type, "attrs":attrs})

#######
# Other config
#######

# --- The rendering vairations
# * All interactions
#interactions = {"a2a" : "all2all"}
# * Only medium interactions
interactions = {"a2m" : "all2media"}
# * Surface/Medium interactions
#interactions = {"a2m" : "all2media", "a2s" : "all2surf"}
# * All interactions details
#interactions = {"s2m" : "surf2media", "s2s" : "surf2surf", "m2m" : "media2media", "m2s" : "surf2media"}

# --- MIS
MIS = {"areaMIS" : [xmlEntry("string", "useMIS", "area")],
       "areaMIS_null" : [xmlEntry("string", "useMIS", "area"),
                         xmlEntry("boolean", "useShiftNull", "true")]} # "noMIS" : "none",

# --- Photons techniques
# * Photons techniques
surfacePhotonCount = "1000000"
volumePhotonCount = "1000000"
beamPhotonCount = "20000"
VRLCount = str(int(volumePhotonCount)//5000)
maxDepth = "12"
rrDepthPhoton = "1"

# * Gather point config
bounceRoughness = "0.05"
initialScaleSurface = "1.0"
alpha = "0.7"

# * Other config
maxPasses = "2000"
dumpIteration = "5"
reconstructAlpha = "0.2"
forceBlackPixels = "true"
maxManifoldIterations = "5"

# Object where all integrators will be added
INTEGRATORS = []
separateReconstruction = True
L1Recons = True
L2Recons = True
directTracing = "false"

# --- Techniques
initialScaleVolumeBASE = 0.1
#volumeTechniques = ["raymarching", "distance", "bre", "beam"]
volumeTechniques = {"BRE" : [xmlEntry("string", "volTechnique", "bre"),
                             xmlEntry("integer", "volumePhotonCount", volumePhotonCount),
                             xmlEntry("float", "initialScaleVolume", str(initialScaleVolumeBASE*1.0))],
                    "VPM" : [xmlEntry("string", "volTechnique", "distance"),
                             xmlEntry("integer", "volumePhotonCount", volumePhotonCount),
                             xmlEntry("float", "initialScaleVolume", str(initialScaleVolumeBASE*1.5))],
                    "Beam" : [xmlEntry("string", "volTechnique", "beam"),
                              xmlEntry("integer", "volumePhotonCount", beamPhotonCount),
                              xmlEntry("float", "initialScaleVolume", str(initialScaleVolumeBASE*1.0))],
                    "Plane" : [xmlEntry("string", "volTechnique", "plane0d"),
                               xmlEntry("integer", "volumePhotonCount", beamPhotonCount),
                               xmlEntry("float", "initialScaleVolume", str(initialScaleVolumeBASE))]}

def copyConfig(c):
    nC = c.copy()
    nC["attrs"] = c["attrs"][:] # Need to deep copy this arg
    return nC

def generateAllInteractionsSPPMVariations(initialConfigs):
    allVar = []
    for initialConfig in initialConfigs:
        for n, value in interactions.items():
            nC = copyConfig(initialConfig)
            if(n == "a2m"):
                nC["attrs"] += [xmlEntry("boolean", "surfaceRendering", "false"),
                                xmlEntry("boolean", "volumeRendering", "true")]
            elif(n == "a2s"):
                nC["attrs"] += [xmlEntry("boolean", "surfaceRendering", "true"),
                                xmlEntry("boolean", "volumeRendering", "false")]
            else:
                print("WARN: NOT POSSIBLE TO HANDLE INTERACTION MODE: ", n)

            if(len(interactions) != 1):
                nC["name"] += "_" + n

            allVar += [nC]
    return allVar

def generateAllInteractionsVariations(initialConfigs):
    allVar = []
    for initialConfig in initialConfigs:
        for n, value in interactions.items():
            nC = copyConfig(initialConfig)
            if(nC["name"] == "PT"):
                nC["attrs"][-1][-1]["attrs"] += [xmlEntry("string", "lightingInteractionMode", value)]
            else:
                nC["attrs"] += [xmlEntry("string", "lightingInteractionMode", value)]

            if(len(interactions) != 1):
                nC["name"] += "_" + n
            allVar += [nC]
    return allVar

def generateDictVariation(initialConfigs, DICTConfig):
    allVar = []
    for initialConfig in initialConfigs:
        for n, xmlArgs in DICTConfig.items():
            nC = copyConfig(initialConfig)
            nC["attrs"] += xmlArgs
            if nC["name"] == "":
                pass
            elif nC["name"][-1] == "-":
                pass
            else:
                nC["name"] += "_"
            nC["name"] += n
            allVar += [nC]
    return allVar

##############################
# SPPM splatting
##############################
SPPMAttrs = [xmlEntry("integer", "maxDepth", maxDepth),
             xmlEntry("integer", "rrDepth", rrDepthPhoton),
             xmlEntry("float", "alpha", alpha),
             xmlEntry("integer", "dumpIteration", dumpIteration),
             xmlEntry("integer", "maxPasses", maxPasses),
             xmlEntry("float", "initialScale", initialScaleSurface),
             xmlEntry("float", "bounceRoughness", bounceRoughness),
             xmlEntry("boolean", "directTracing", directTracing),
             xmlEntry("integer", "minDepth", "0"),
             xmlEntry("float", "cameraSphere", cameraSphere)]

SPPMIntegrators = [{"type" : "sppm",
                  "name" : "",
                  "attrs" : SPPMAttrs +
                            [xmlEntry("integer", "photonCount", surfacePhotonCount)]}]

SPPMIntegrators = generateAllInteractionsSPPMVariations(SPPMIntegrators)
SPPMIntegrators = generateDictVariation(SPPMIntegrators, volumeTechniques)
INTEGRATORS += SPPMIntegrators

##############################
# BDPT
##############################
# - BDPT doesn't works for now
BDPTAttrs = [xmlEntry("integer", "maxDepth", maxDepth),
             xmlEntry("integer", "minDepth", "0"),
            xmlEntry("integer", "rrDepth", rrDepthPaths),
            xmlEntry("string", "lightingInteractionMode","all2media")]
BDPTAvgAttrs = [xmlEntry("integer", "maxPasses", maxPasses),
               xmlEntry("integer", "maxRenderingTime", timeMax),
               xmlEntry("integer", "iterationMult", multIterationBDPT),
               xmlIntAttrs("bdpt", BDPTAttrs)]
BDPTIntegrators = {"type" : "avg",
                 "name" : "BDPT",
                 "attrs" : BDPTAvgAttrs,
                 "samples" : samplesBDPT} # Rewritting samples counts
INTEGRATORS.append(BDPTIntegrators)

##############################
# VRL
##############################
#VRLAttrs = [xmlEntry("integer", "maxDepth", maxDepth),
#            xmlEntry("integer", "rrDepth", rrDepthPhoton),
#            xmlEntry("boolean", "autoCancelGathering", "false"),
#            xmlEntry("integer","globalPhotons", VRLCount) # Use the same number of photon beams
#            ]
#VRLAvgAttrs = [
#    xmlEntry("integer", "maxPasses", maxPasses),
#    xmlEntry("integer", "maxRenderingTime", timeMax),
#    xmlEntry("boolean", "twostepalgo", "true"), # We need to call preprocess again and again
#    xmlIntAttrs("vrl", VRLAttrs)
#]
#VRLIntegrators = [{"type" : "avg",
#                  "name" : "VRL",
#                  "attrs" : VRLAvgAttrs,
#                  "samples" : samplesVRL}]
#TODO: Do the variations
#INTEGRATORS += VRLIntegrators

##############################
# PT
##############################
PTAttrs = [xmlEntry("integer", "maxDepth", maxDepth),
           xmlEntry("integer", "rrDepth", rrDepthPaths)]
PTAvgAttrs = [xmlEntry("integer", "maxPasses", maxPasses),
              xmlEntry("integer", "maxRenderingTime", timeMax),
              xmlEntry("integer", "iterationMult", multIterationBDPT),
              xmlIntAttrs("volpath", PTAttrs)]
PTIntegrators = [{"type" : "avg",
                "name" : "PT",
                "attrs" : PTAvgAttrs,
                "samples" : samplesPT}]

PTIntegrators = generateAllInteractionsVariations(PTIntegrators)
INTEGRATORS += PTIntegrators

##############################
# Gradient domain
##############################
GRADIENTAttrs = [xmlEntry("float", "shiftThreshold", "0.001"),
                 xmlEntry("float", "reconstructAlpha", reconstructAlpha),
                 xmlEntry("boolean", "forceBlackPixels", forceBlackPixels),
                 xmlEntry("integer", "maxManifoldIterations", maxManifoldIterations),
                 xmlEntry("boolean", "directTracing", directTracing)]

GRADIENTRecons = [("",[xmlEntry("boolean", "reconstructL1", "true"),
                      xmlEntry("boolean", "reconstructL2", "true")])]
if separateReconstruction:
    GRADIENTRecons = []
    if(L1Recons):
        GRADIENTRecons += [("L1", [xmlEntry("boolean", "reconstructL1", "true"),
                                   xmlEntry("boolean", "reconstructL2", "false")])]
    if(L2Recons):
        GRADIENTRecons += [("L2", [xmlEntry("boolean", "reconstructL2", "true"),
                                   xmlEntry("boolean", "reconstructL1", "false")])]

for name, reconsAttrib in GRADIENTRecons:
    if(name != ""):
        name = "_"+name

    ##############################
    # GBDPT
    ##############################

    GRADIENT_BDPT_Attrs = GRADIENTAttrs[:] + reconsAttrib[:] + \
                          [xmlEntry("integer", "maxDepth", maxDepth),
                           xmlEntry("integer", "rrDepth", rrDepthPaths),
                           xmlEntry("boolean", "lightImage", "true"),
                           xmlEntry("integer", "dumpIteration", dumpIteration),
                           xmlEntry("integer", "iterationMult", multIterationBDPT)]

    #FIXME: Add max time and passes
    GRADIENT_BDPT_Integrators = [{"type" : "gbdpt",
                                "name" : "G-BDPT"+name,
                                "attrs" : GRADIENT_BDPT_Attrs,
                                "samples" : samplesGBDPT, # Rewritting samples counts
                                "filmType" : "multifilm"}]

    GRADIENT_BDPT_Integrators = generateAllInteractionsVariations(GRADIENT_BDPT_Integrators)
    INTEGRATORS += GRADIENT_BDPT_Integrators

    ##############################
    # G-PT
    ##############################
    GRADIENT_PT_Attrs = GRADIENTAttrs[:] + reconsAttrib[:] + \
                          [xmlEntry("integer", "maxDepth", maxDepth),
                           xmlEntry("integer", "rrDepth", rrDepthPaths),
                           xmlEntry("integer", "dumpIteration", dumpIteration),
                           xmlEntry("integer", "iterationMult", multIterationBDPT)]

    GRADIENT_PT_Integrators = [{"type" : "gpt",
                                "name" : "G-PT"+name,
                                "attrs" : GRADIENT_PT_Attrs,
                                "samples" : samplesGPT, # Rewritting samples counts
                                "filmType" : "multifilm"}]

    GRADIENT_BDPT_Integrators = generateAllInteractionsVariations(GRADIENT_PT_Integrators)
    INTEGRATORS += GRADIENT_BDPT_Integrators

    ##############################
    # GPM
    ##############################
    GVPMAttrs = GRADIENTAttrs[:] + reconsAttrib[:] + \
                [xmlEntry("integer", "maxDepth", maxDepth),
                 xmlEntry("integer", "rrDepth", rrDepthPhoton),
                 xmlEntry("float", "alpha", alpha),
                 xmlEntry("integer", "photonCount", surfacePhotonCount),
                 xmlEntry("integer", "dumpIteration", dumpIteration),
                 xmlEntry("integer", "maxPasses", maxPasses),
                 xmlEntry("float", "initialScale", initialScaleSurface),
                 xmlEntry("float", "bounceRoughness", bounceRoughness),
                 xmlEntry("integer", "minDepth", "0"),
                 xmlEntry("float", "cameraSphere", cameraSphere)]

    GVPMIntegrators = [{"type" : "gvpm",
                      "name" : "G-",
                      "attrs" : GVPMAttrs}]

    GVPMIntegrators = generateAllInteractionsVariations(GVPMIntegrators)
    GVPMIntegrators = generateDictVariation(GVPMIntegrators, volumeTechniques)

    # Add the reconstruction technique
    for k in range(len(GVPMIntegrators)):
        GVPMIntegrators[k]["name"] += name

    GVPMIntegrators = generateDictVariation(GVPMIntegrators, MIS)
    INTEGRATORS += GVPMIntegrators
