#######
# Global config
#######
# --- Path tracing techniques
rrDepthPaths = "12"
timeMax = "3700" # 1h + 100 sec
samplesPT = "32"
samplesBDPT = "4"

# --- SPPM options (basic)
# * Photons config
photonCountSPPMSplat = "10000000"
photonCountGPM = str(int(photonCountSPPMSplat)//10)       # ensure gather is the same for both SPPM and GPM
maxDepth = "12"
rrDepthPhoton = "12"

# * Gather point config
bounceRoughness = "0.05"
initialScale = "1.0"
alpha = "0.9"

# * Other config
maxPasses = "2000"
dumpIteration = "5"
reconstructAlpha = "0.2"
forceBlackPixels = "true"
maxManifoldIterations = "5"

# Object where all integrators will be added
INTEGRATORS = []
separateReconstruction = True
directTracing = "false"
##############################
# Functions
##############################
def xmlEntry(type, name, value):
    return (type,{"name":name,"value":value})

def xmlIntAttrs(type, attrs):
    return ("integrator",{"type":type, "attrs":attrs})

##############################
# SPPM splatting
##############################
SPPMAttrs = [xmlEntry("integer", "maxDepth", maxDepth),
             xmlEntry("integer", "rrDepth", rrDepthPhoton),
             xmlEntry("float", "alpha", alpha),
             xmlEntry("integer", "dumpIteration", dumpIteration),
             xmlEntry("integer", "maxPasses", maxPasses),
             xmlEntry("float", "initialScale", initialScale),
             xmlEntry("float", "bounceRoughness", bounceRoughness),
             xmlEntry("boolean", "directTracing", directTracing)]

SPPMSplatIntegrator = {"type" : "sppm_splat",
                  "name" : "SPPMSplat",
                  "attrs" : SPPMAttrs +
                            [xmlEntry("integer", "photonCount", photonCountSPPMSplat)]}
INTEGRATORS.append(SPPMSplatIntegrator)


SPPMIntegrator = {"type" : "sppm",
                  "name" : "SPPM",
                  "attrs" : SPPMAttrs +
                            [xmlEntry("integer", "photonCount", photonCountGPM)]}
INTEGRATORS.append(SPPMIntegrator)

##############################
# BDPT
##############################
BDPTAttrs = [xmlEntry("integer", "maxDepth", maxDepth),
             xmlEntry("integer", "rrDepth", rrDepthPaths)]
BDPTAvgAttrs = [xmlEntry("integer", "maxPasses", maxPasses),
                xmlEntry("integer", "maxRenderingTime", timeMax),
                xmlIntAttrs("bdpt", BDPTAttrs)]
BDPTIntegrator = {"type" : "avg",
                  "name" : "BDPT",
                  "attrs" : BDPTAvgAttrs,
                  "samples" : samplesBDPT} # Rewritting samples counts
INTEGRATORS.append(BDPTIntegrator)

##############################
# PT
##############################
PTAttrs = [xmlEntry("integer", "maxDepth", maxDepth),
           xmlEntry("integer", "rrDepth", rrDepthPaths)]
PTAvgAttrs = [xmlEntry("integer", "maxPasses", maxPasses),
              xmlEntry("integer", "maxRenderingTime", timeMax),
              xmlIntAttrs("path", PTAttrs)]
PTIntegrator = {"type" : "avg",
                "name" : "PT",
                "attrs" : PTAvgAttrs,
                "samples" : samplesPT} # Rewritting samples counts

INTEGRATORS.append(PTIntegrator)

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
    GRADIENTRecons = [("L1", [xmlEntry("boolean", "reconstructL1", "true"),
                              xmlEntry("boolean", "reconstructL2", "false")]),
    ("L2", [xmlEntry("boolean", "reconstructL2", "true"),
            xmlEntry("boolean", "reconstructL1", "false")])]

for name, reconsAttrib in GRADIENTRecons:
    if(name != ""):
        name = "_"+name
    ####### PT
    GRADIENT_PT_Attrs = GRADIENTAttrs[:] + reconsAttrib[:] + \
                        [xmlEntry("integer", "maxDepth", maxDepth),
                         xmlEntry("integer", "rrDepth", rrDepthPaths),
                         xmlEntry("integer", "dumpIteration", "1")]

    #FIXME: Add max time and passes
    GRADIENT_PT_Integrator = {"type" : "gpt",
                              "name" : "GPT"+name,
                              "attrs" : GRADIENT_PT_Attrs,
                              "samples" : samplesPT, # Rewritting samples counts
                              "filmType" : "multifilm"}
    INTEGRATORS.append(GRADIENT_PT_Integrator)

    ####### BDPT
    GRADIENT_BDPT_Attrs = GRADIENTAttrs[:] + reconsAttrib[:] + \
                        [xmlEntry("integer", "maxDepth", maxDepth),
                         xmlEntry("integer", "rrDepth", rrDepthPaths),
                         xmlEntry("boolean", "lightImage", "true"),
                         xmlEntry("integer", "dumpIteration", "1")]

    #FIXME: Add max time and passes
    GRADIENT_BDPT_Integrator = {"type" : "gbdpt",
                              "name" : "GBDPT"+name,
                              "attrs" : GRADIENT_BDPT_Attrs,
                              "samples" : samplesBDPT, # Rewritting samples counts
                              "filmType" : "multifilm"}
    INTEGRATORS.append(GRADIENT_BDPT_Integrator)

    ##############################
    # GPM
    ##############################
    GPMAttrs = GRADIENTAttrs[:] + reconsAttrib[:] + \
                [xmlEntry("integer", "maxDepth", maxDepth),
                 xmlEntry("integer", "rrDepth", rrDepthPhoton),
                 xmlEntry("float", "alpha", alpha),
                 xmlEntry("integer", "photonCount", photonCountGPM),
                 xmlEntry("integer", "dumpIteration", dumpIteration),
                 xmlEntry("integer", "maxPasses", maxPasses),
                 xmlEntry("float", "initialScale", initialScale),
                 xmlEntry("float", "bounceRoughness", bounceRoughness),
                 xmlEntry("integer", "dumpIteration", "5")]

    GPMIntegrator = {"type" : "gpm",
                      "name" : "GPM"+name,
                      "attrs" : GPMAttrs}
    INTEGRATORS.append(GPMIntegrator)
