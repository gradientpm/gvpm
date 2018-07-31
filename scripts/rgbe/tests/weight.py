import rgbe.io
import rgbe.fast
import rgbe.utils
import Image
import optparse
import math
import matplotlib.pyplot as plt

def lum(p):
    return 0.21268*p[0] + 0.7152*p[1] + 0.0722*p[2]

def imgContrib(p1Img, p2Img, h, w):
    data = []
    for x in range(h):
        tmp = []
        for y in range(w):
            p1 = lum(p1Img[x*w+y])
            p2 = lum(p2Img[x*w+y])
            s = (p1+p2)
            if(s == 0.0):
            	tmp.append(0.5)
            else:
            	tmp.append(p1 / s)
        data.append(tmp)
    return (data)

def setupDiffFig(w,h,data):
    fig = plt.figure(figsize=(((1.1*w)/64), h/64), dpi=64)
    a = plt.Axes(fig, [0., 0., 1., 1.])
    
    a.set_axis_off()
    fig.add_axes(a)
    
    cax = a.imshow(data, interpolation='nearest', vmin=0, vmax=1.0)
    extent = a.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    return fig,extent

parser = optparse.OptionParser()
parser.add_option('-i','--input1', help="First image")
parser.add_option('-j','--input2', help="Second image")
(opts,args) = parser.parse_args()

# We read the two HDR images
(widthHDR1, heightHDR1),imgHDR1 = rgbe.io.read(opts.input1);
(widthHDR2, heightHDR2),imgHDR2 = rgbe.io.read(opts.input2);

if (widthHDR1 != widthHDR2 or heightHDR1 != heightHDR2):
	print("The two HDR images don't have the same size. Aborting.")
	exit()

imgContrib1 = imgContrib(imgHDR1,imgHDR2, heightHDR1, widthHDR1)
fig,extent = setupDiffFig(widthHDR1,heightHDR1,imgContrib1)
plt.show()

