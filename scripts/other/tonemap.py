import rgbe.io
import rgbe.utils
try:
    import Image
except ImportError:
    from PIL import Image
	
import sys 

def copyPixtoPil(pix, im):
    pInt = [(int(c[0]*255),int(c[1]*255),int(c[2]*255)) for c in pix]
    im.putdata(pInt)
	
filenameHDR = sys.argv[1]
filenameIMG = sys.argv[2]
exposure = 6

(width,height),p = rgbe.io.read(filenameHDR)
rgbe.utils.applyExposureGamma(p, exposure, 2.2)

im = Image.new("RGB", (width,height))
copyPixtoPil(p, im)
im.save(filenameIMG, optimize=True)

