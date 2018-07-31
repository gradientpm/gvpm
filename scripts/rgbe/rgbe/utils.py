import math

#####
##### Norm class
#####
class EmptyNorm(object):
    def __init__(self):
        pass
    
    def diff(self, c):
        return 1

class RMSENorm(EmptyNorm):
    def __init__(self):
        EmptyNorm.__init__(self)
        self.rmse = 0.0
        
    def diff(self, c):
        diff = math.sqrt( c[0]*c[0] + c[1]*c[1] + c[2]*c[2] )
        distance = abs(diff)
        self.rmse += diff * diff
        return distance

####
#### Color
####

class EmptyFakeColor(object):
    def __init__(self):
        pass
    
    def getColor(self, v):
        "Color coded error function"
        pass
    
class FakeRedColor(EmptyFakeColor):
    def __init__(self,min=0.0,max=1.0):
        EmptyFakeColor.__init__(self)
        self.max = max
        self.min = min
        
    def getColor(self,v):
        #white
        r = 1.
        g = 1.
        b = 1.
    
        if v < self.min:
            v = self.min
        if v > self.max:
            v = self.max
        dv = self.max - self.min
        
        if v < (self.min + 0.25 * dv):
            r = 0
            g = 4 * (v - self.min) / dv
        elif v < (self.min + 0.5 * dv):
            r = 0;
            b = 1 + 4 * (self.min + 0.25 * dv - v) / dv
        elif v < (self.min + 0.75 * dv):
            r = 4 * (v - self.min - 0.5 * dv) / dv
            b = 0;
        else:
            g = 1 + 4 * (self.min + 0.75 * dv - v) / dv
            b = 0;
        
        return (r, g, b)

####
#### Compatibility functions
####

def copyPixeltoPIL(width, height, pixels, im):
#     for x in range(width):
#         for y in range(height):
#             c = pixels[y*width+x]
#             pixelExp = (int(c[0]*255),
#                         int(c[1]*255),
#                         int(c[2]*255))
#             im[x,y] = pixelExp
    pInt = [(int(c[0]*255),int(c[1]*255),int(c[2]*255)) for c in pixels]
    im.putdata(pInt)

####
#### Image manipulation methods
####

def applyExposureGamma(pixels, exposure = 1.0, gamma = 2.2):
#     def expo(p,exp,invG):
#         return (math.pow(p[0]*exp,invG),
#                 math.pow(p[1]*exp,invG),
#                 math.pow(p[2]*exp,invG))
    exp = math.pow(2, exposure)
    invG = 1.0/gamma
#     return map((lambda x: expo(x,exp,invG)), pixels)
    for i in range(len(pixels)):
        p = pixels[i]
        pixels[i] = (math.pow(p[0]*exp,invG),
                     math.pow(p[1]*exp,invG), 
                     math.pow(p[2]*exp,invG))

####
#### Compute methods
####

def diff(p1, p2):
    if(len(p1) != len(p2)):
        raise Exception("Size mismatch")
    
    res = [0]*len(p1)
    
    for i in range(len(p1)):
        pixel = p1[i]
        pixelRef = p2[i]
        
        Rdiff = pixel[0] - pixelRef[0]
        Gdiff = pixel[1] - pixelRef[1]
        Bdiff = pixel[2] - pixelRef[2]
        
        res[i] = (Rdiff, Gdiff, Bdiff)
        
    return res

def computeNorm(p1, p2, norm):
    d = diff(p1,p2)
    
    if(not isinstance(norm, EmptyNorm)):
        raise Exception("Need define Norm as EmptyNormHerit")
    
    n = [0]*len(d)
    for i in range(len(d)):
        n[i] = norm.diff(d[i])
    
    return n

def computeNormFakeColor(p1, p2, norm, fakeColor):
    n = computeNorm(p1, p2, norm)
    
    if(not isinstance(fakeColor, EmptyFakeColor)):
        raise Exception("Need define fakeColor as EmptyNormHerit")
    
    for i in range(len(n)):
        n[i] = fakeColor.getColor(n[i])
    
    return n

