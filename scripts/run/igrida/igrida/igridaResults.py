import os, sys, optparse, subprocess
import rgbe.merge
import glob

def merge(width, height, blocksize, inputFile, output, name="", ext="hdr"):
    rgbe.merge.merge(inputFile,int(width),int(height),int(blocksize), output, ext)

def sumblock(w, h, blockSize, path, outFilename, ext="hdr"):
    w = int(w)
    h = int(h)
    blockSize = int(blockSize)
    pix = []
    
    for i in range(w*h):
        pix.append((0.0,0.0,0.0))
    
    files = glob.glob(path+"*."+ext)
    norm = 0
    for localFile in files:
            # Read and copy all pixels
            print('Read (%s)' % (os.path.basename(localFile)))
            (wLocal,hLocal), pLocal = rgbe.io.read(localFile)
            if(wLocal != w and hLocal != h):
                print("[WARN] size mismatch (%i, %i) for block (%s)" % (wLocal, hLocal, localFile))
            else:
                norm += 1
                for pLoc in range(0,w*h):
                        pix[pLoc] = (pLocal[pLoc][0] + pix[pLoc][0],
                                     pLocal[pLoc][1] + pix[pLoc][1],
                                     pLocal[pLoc][2] + pix[pLoc][2])
    
    # Normalisation contrib
    if(norm != 0):
        print("[INFO] Make normalisation with %i" % (norm))
        for pLoc in range(0,w*h):
                pix[pLoc] = (pix[pLoc][0] / norm,
                             pix[pLoc][1] / norm,
                             pix[pLoc][2] / norm)
    # Write the final image
    rgbe.io.write(outFilename, w, h, pix)

def getLum(p):
    lum = 0.3*p[0] + 0.3*p[1] + 0.3*p[2]
    return lum

def sumblockRobust(w, h, blockSize, path, outFilename, ext="hdr", maxNb = 16):
    w = int(w)
    h = int(h)
    blockSize = int(blockSize)
    pix = []
    pixMax = []
    
    for i in range(w*h):
        pix.append((0.0,0.0,0.0))
        pixMax.append((0.0,(0.0,0.0,0.0)))
        
    files = glob.glob(path+"*."+ext)
    norm = 0
    for localFile in files:
        if(norm >= maxNb):
            break
        # Read and copy all pixels
        print('Read (%s)' % (os.path.basename(localFile)))
        (wLocal,hLocal), pLocal = rgbe.io.read(localFile)
        if(wLocal != w and hLocal != h):
            print("[WARN] size mismatch (%i, %i) for block (%s)" % (wLocal, hLocal, localFile))
        else:
            norm += 1
            for pLoc in range(0,w*h):
                    lum = getLum(pLocal[pLoc])
                    if(lum > pixMax[pLoc][0]):
                        pix[pLoc] = (pixMax[pLoc][1][0] + pix[pLoc][0],
                                 pixMax[pLoc][1][1] + pix[pLoc][1],
                                 pixMax[pLoc][1][2] + pix[pLoc][2])
                        pixMax[pLoc] = (lum, pLocal[pLoc])
                    else:
                        pix[pLoc] = (pLocal[pLoc][0] + pix[pLoc][0],
                                 pLocal[pLoc][1] + pix[pLoc][1],
                                 pLocal[pLoc][2] + pix[pLoc][2])
    
    # Normalisation contrib
    norm -= 1
    if(norm > 0):
        print("[INFO] Make normalisation with %i" % (norm))
        for pLoc in range(0,w*h):
                pix[pLoc] = (pix[pLoc][0] / norm,
                             pix[pLoc][1] / norm,
                             pix[pLoc][2] / norm)
    
    
    # Write the final image
    rgbe.io.write(outFilename, w, h, pix)

   
def merge_result(options):
    out = os.path.dirname(options.output)
    robustSum = int(options.userobustsum)
    if(not os.path.exists(out)):
        print("Create output directory:",out)
        os.makedirs(out)
    
    if(options.onlyone):
        print("[DEBUG] Only one mode")
        if(not os.path.isdir(options.input)):
            print("[WARN] Impossible to find directory: " + options.input)
            return
        outputFile = options.output
        #print(options.name)
        #for name in options.name:
        #print(name)
        nameOut = ".".join(outputFile.split(".")[:-1])+""+"."+outputFile.split(".")[-1]
        if(options.usesum):
            sumblock(options.width, options.height, options.blocks, options.input, os.path.abspath(nameOut), options.extorig)
        elif(robustSum != -1):
            sumblockRobust(options.width, options.height, options.blocks, options.input, os.path.abspath(nameOut), options.extorig, robustSum)
        else:
            merge(options.width, options.height, options.blocks, options.input, os.path.abspath(nameOut), "", options.extorig)
    else:
        beg = int(options.beginFrame)
        end = int(options.endFrame)
        for i in range(beg, end):
            inputFile = os.path.dirname(options.input) + os.path.sep + str(i)
            if(not os.path.isdir(inputFile)):
                print("[WARN] Impossible to find directory: " + inputFile)
                continue
            inputFile += os.path.sep
            
            #for name in options.name:
            outputFile = out + os.path.sep + str(i).zfill(5) + "" + "." + options.extdest
            print("[TRACE] Merge for " + outputFile) 
            if(options.usesum):
                sumblock(options.width, options.height, options.blocks, inputFile, os.path.abspath(outputFile), options.extorig)
            elif(robustSum != -1):
                sumblockRobust(options.width, options.height, options.blocks, inputFile, os.path.abspath(outputFile), options.extorig, robustSum)
            else:
                merge(options.width, options.height, options.blocks, inputFile, os.path.abspath(outputFile), "", options.extorig)
        
    
if __name__=="__main__":
    parser = optparse.OptionParser()
    parser.add_option('-x','--width', help='image final width [default=1920]', default="1920")
    parser.add_option('-y','--height', help='image final height [default=1080]', default="1080")
    parser.add_option('-f','--beginFrame', help='begin frame of merging')
    parser.add_option('-b','--blocks', help='begin frame of merging [default=32]', default = "32")
    parser.add_option('-e','--endFrame', help='end frame of merging')
    parser.add_option('-1','--onlyone', help='end frame of merging', default=False, action="store_true")
    parser.add_option('-i','--input', help='input directory')
    parser.add_option('-o','--output', help='output directory or output filename')
    #parser.add_option('-n','--name', help='name of hdr files suffix', action='append', default=[''])
    parser.add_option('-s','--extorig', help='orignial extension', default="hdr")
    parser.add_option('-c','--extdest', help='destination extension', default="hdr")
    parser.add_option('-p','--usesum', help="use sum instead merge", default=False, action="store_true")
    parser.add_option('-r','--userobustsum', help="use robust sum instead merge", default=-1)
    
    
    (options, args) = parser.parse_args()
    
    if not ((options.beginFrame and options.endFrame) or options.onlyone):
        parser.error("not all informations is specified (frame beg/end || onlyone)")
    if not(options.input and options.output):
        parser.error("not all informations is specified (input/output)")
    
    merge_result(options)
    
    
