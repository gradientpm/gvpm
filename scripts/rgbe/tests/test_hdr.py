"""
Python class in order to read RADIANCE image files.
This implementation its inspired by 
"""

import math
import rgbe.io
import rgbe.utils
import rgbe.fast
try:
    import Image
except ImportError:
    from PIL import Image

def tonemap(path, dest, exposure, gamma):
    (width,height),p = rgbe.io.read(path)
    print("[DEBUG] Read HDR image ",width,"x",height," (exp:", exposure, ")")
    rgbe.utils.applyExposureGamma(p, exposure, gamma)
    
    im = Image.new("RGB", (width,height)) 
    rgbe.utils.copyPixeltoPIL(width, height, p, im)
    im.save(dest)

def tonemap_fast(path, dest, exposure, gamma):
    print("[DEBUG] Fast Read HDR image")
    (width,height),p = rgbe.io.read_tonemap(path, gamma, exposure)
    im = Image.new("RGB", (width,height)) 
    im.putdata(p)
    im.save(dest)

def scale(path,dest,mult):
    (width,height),p = rgbe.io.read(path)
    
    print("[DEBUG] scale image ",width,"x",height," (mult:", mult, ")")
    for x in range(width):
        for y in range(height):
            pixel = p[y*width+x]
            p[y*width+x] = (pixel[0]*mult,
                            pixel[1]*mult,
                            pixel[2]*mult)
    
    rgbe.io.write(dest, width, height, p)
    
    (width,height),p = rgbe.io.read(dest)
 
def diffHDR(path, pathRef, dest, scale):
    "Compare path and ref HDR files, compute the difference times scale and write it into dest file"
    (widthRef,heightRef),pRef = rgbe.io.read(pathRef)
    (width,height),p = rgbe.io.read(path)
       
    if widthRef != width or heightRef != height:
        print("ref size (", widthRef, "x",heightRef,") and (", width, "x",height,") mismatched")
    else:
        # Compute RMSE
        rmse = rgbe.utils.RMSENorm()
        color = rgbe.utils.FakeRedColor(max=scale)
        fakeIm = rgbe.utils.computeNormFakeColor(pRef, p, rmse, color)
        
        # Write image
        im = Image.new("RGB", (width,height)) 
        rgbe.utils.copyPixeltoPIL(width, height, fakeIm, im)  
            
        print("[INFO] RMSE = ", rmse.rmse / (width*height))
        im.save(dest)
        
def test_rmse_all_images(images, ref):
    (widthRef,heightRef),pRef = rgbe.io.read(ref)
    print(widthRef, heightRef)
    metrics = rgbe.fast.rmse_all_images(widthRef, heightRef, images, pRef, 1.0, None)
    print(metrics)

if __name__=="__main__":
    tonemap("test.hdr", "test.jpg", 8, 2.2)
    tonemap_fast("test.hdr", "test_fast.jpg", 8, 2.2)
    scale("test.hdr", "test_256.hdr", 1.0)
    diffHDR("compare.hdr", "ref.hdr", "diff.png", 1)
    test_rmse_all_images(["img1.hdr","img2.hdr"], "test.hdr")
    