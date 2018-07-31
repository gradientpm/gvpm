import optparse
import matplotlib.pyplot as plt
import rgbe.io
from matplotlib import cm
import math
from glob import glob
import os
try:
    import Image
    import ImageDraw
except ImportError:
    from PIL import Image
    from PIL import ImageDraw


def convertImage(p, h, w, inver):
    data = []
    for x in range(h):
        tmp = []
        for y in range(w):
            p1 = 1-(p[x*w+y][0])
            tmp.append(p1)
        data.append(tmp)
    return data
def convertImageImp(path, out, 
                    clMin = -1, clMax = -1, inver = False, 
                    usePourcentage = False, pourcent = 0.90):
    (w, h),pRef = rgbe.io.read(path)
    
    fig = plt.figure(figsize=((w/100.0), (h/100.0)), dpi=100)

    data = convertImage(pRef, h, w, inver)
    
    pRefLum = [p[0] for p in pRef]
    pRefLum.sort()
    
    maxData = pRefLum[-1]
    minData = pRefLum[0]
    
    if(usePourcentage):
        maxData = pRefLum[int(len(pRefLum)*pourcent)]

    print("Find the max: "+str(maxData))
    print("Find the min: "+str(minData))
    
    if clMin >= 0:
    	minData = clMin
    if clMax >= 0:
    	maxData = clMax

    #print(data)
    cax = plt.figimage(data, vmin=minData, vmax=maxData, cmap=cm.get_cmap("viridis"))
    fig.savefig(out)#, bbox_inches=extent)
    plt.close()
    
    im = Image.open(out)
    (widthN, heightN) = im.size
    im = im.crop(((widthN-w), 
                  (heightN-h),
                  w,
                  h))
    im.save(out)
    im.close()
    
    return maxData,minData

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('-f', '--filename', help='filename')
    parser.add_option('-o', '--output', help='output file')
    parser.add_option('-u', '--maxclamp', help='max clamping of the color bar (u for up)', default=-1)
    parser.add_option('-d', '--minclamp', help='min clamping of the color bar (d for down)', default=-1)
    parser.add_option('-p','--pourcentage', help='Use percentage to find max', default=False, action="store_true")
    parser.add_option('-i', '--inverse', help='compute inverse value', default=-1)
    (opts, args) = parser.parse_args()
    
    minClamping = float(opts.minclamp)
    maxClamping = float(opts.maxclamp)
    inv = int(opts.inverse)

    convertImageImp(opts.filename, opts.output, minClamping, maxClamping,inv,opts.pourcentage)
