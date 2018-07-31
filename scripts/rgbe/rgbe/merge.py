import rgbe.io
import os

def merge(path, w, h, blockSize, outFilename, ext = "hdr"):

    # Read all images
    pix = [0.0]*(w*h)
    for x in range(0,w,blockSize):
        for y in range(0,h,blockSize):
            localFile = path + str(x) + "_" + str(y) + "." + ext
            if(os.path.exists(localFile)):
                # Read and copy all pixels
                (wLocal,hLocal), pLocal = rgbe.io.read(localFile)
                for xLoc in range(x,x+wLocal):
                    for yLoc in range(y,y+hLocal):
                        pix[yLoc*w + xLoc] = pLocal[(yLoc-y)*wLocal + (xLoc-x)]
            else:
                print("[WARN] (%i,%i) is missing" % (x,y))
                
    # Write the final image
    rgbe.io.write(outFilename, w, h, pix)
    