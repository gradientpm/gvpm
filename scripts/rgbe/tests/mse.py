import rgbe.io
import rgbe.fast
import rgbe.utils
import optparse

try:
	import Image
except ImportError:
	from PIL import Image

parser = optparse.OptionParser()
parser.add_option('-i','--input1', help="First image")
parser.add_option('-j','--input2', help="Second image")
(opts,args) = parser.parse_args()

# We read the two HDR images
(widthHDR1, heightHDR1),imgHDR1 = rgbe.io.read(opts.input1);
(widthHDR2, heightHDR2),imgHDR2 = rgbe.io.read("global_pass_10.hdr");

if (widthHDR1 != widthHDR2 or heightHDR1 != heightHDR2):
	print("The two HDR images don't have the same size. Aborting.")
	exit()
# We read the mask image
imgMask = Image.open("masktest.png")
# imgMask.show()

if (imgMask.size[0] != widthHDR1 or imgMask.size[1] != heightHDR2):
	print("The mask image doesn't have the same size as the HDR images. Aborting.")
	exit()

imgMaskData = list(imgMask.getdata());


print("The image size is: " + str(widthHDR1) + " x " + str(heightHDR1))

# We test the fast library
rmsevalue, imgDiffData = rgbe.fast.rmse(widthHDR1, heightHDR1, imgHDR1, imgHDR2, 10.0, imgMaskData)
print("RMSE=" + str(rmsevalue))

imgDiff = Image.new("RGB", (widthHDR1, heightHDR1))
rgbe.utils.copyPixeltoPIL(widthHDR1, heightHDR1, imgDiffData, imgDiff);
imgDiff.save("diff.png")

 

