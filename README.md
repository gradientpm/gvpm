# Gradient-domain Volumetric Photon Density Estimation

![](https://beltegeuse.github.io/research/img/publications/GradientVolumetricPM.png)

This is the code release for the paper [Gradient-domain Volumetric Photon Density Estimation](http://beltegeuse.s3-website-ap-northeast-1.amazonaws.com/research/2018_GVPM.pdf) in SIGGRAPH 2018. 

It extends Mitsuba 0.5.0 to implement a group of rendering techniques to render homogeneous participating media.
The code can be compiled on Windows 10 with Visual Studio 2013, and Arch Linux platform. It is preferable to use CMake to compile this project.

## Download

- [Paper](http://beltegeuse.s3-website-ap-northeast-1.amazonaws.com/research/2018_GVPM.pdf)
- [Scene data and reference images](http://beltegeuse.s3-website-ap-northeast-1.amazonaws.com/research/2018_GVPM/comparison/index.html)
- Mitsuba dependencies
: [Windows](https://www.mitsuba-renderer.org/repos/dependencies_windows) 
and [Mac](https://www.mitsuba-renderer.org/repos/dependencies_macos).
  
## Photon Density Integrators

We support rendering of participating media in the primal domain with the `sppm` integrator, and in the gradient domain with the `gvpm` integrator. In each integrator, several photon representations are implemented, including photon points, beams, and planes. 

#### Volumetric Photon Mapping (VPM or G-VPM)
This is basically the surface-based photon mapping technique brought into volumetric rendering. It makes use of a uniform 3D kernel for photon gathering.

#### Beam Radiance Estimate (BRE or G-BRE)
In this representation, we treat the camera rays as beams, and gather all photons that the beams intersect. 
We support gathering with a 2D or a 3D kernel. It is preferable to use the 3D kernel as it allows spatial relaxation during gathering, i.e., the proposed mixed shift in the paper.

#### Photon Beams (Beams or G-Beams)
This representation treats both camera and light rays as beams. We support gathering with a 1D or a 3D kernel. Similar to BRE, it is preferable to use a 3D kernel for spatial relaxations.

#### (Experimental) Photon planes (Planes or G-Planes)
This representation treats the light rays as planes. 
The current implementation does not check the visibility between the photon plane and the camera ray. For this reason, this technique only works with scenes that skipping visibility check does not bring large errors, e.g., the LASER scene in the paper. We support 0D kernel to gather plane contribution.

## Path-based Integrators

Beyond primal domain path tracing and bidirectional path tracing that naturally handles participating media, 
we modified gradient-domain path tracing `gpt` to support homogeneous participating media. 
There is also code extended from gradient-domain bidirectional path tracing `gbdpt` (experimental).

## Known issues

Due to time restriction, the current code version has few issues (ordered by priorities). These will be addressed if time permits. 
Note that these issues do not impact the results produced in our paper. If you want to contribute, please, feel free to address these issues through pull requests.

- Surfaces rendering are not handling correctly in this code version for photon density techniques. Only media to media or surface to media light transports are considered.
- The code only supports area light sources.
- Some restrictions on BSDFs: "mixture bsdf" can handle only two different component. "two-sided bsdf" only handles the case when the same BSDF is used on the two faces surface. 
- G-PT: When surface rendering is enabled, direct-lighting computation leads to inaccurate gradients. This problem might be due to BSDF component selection code.
- G-PT: Does not include the optimized routine when an interface shadow the light source.
- G-BDPT: Does not handle scenes with interfaces (due to unmanaged MIS computation).
- (G-)Plane: visibility support.
- ~~Support heterogeneous participating media.~~ (G-VPM heterogenous participating media is still missing)

License
=======
This code is released under the GNU General Public License (version 3).

This source code includes the following open source implementations:

- Screened Poisson reconstruction code from NVIDIA, released under the new BSD license.
- Mitsuba 0.5.0 by Wenzel Jakob, released under the GNU General Public License (version 3).

Citation
========

If you use this code, please consider citing the following works accordingly: 

```
@article{gruson:2018:gdvpm,
 title = {{Gradient-domain Volumetric Photon Density Estimation}},
 author = {Gruson, Adrien and Hua, Binh-Son and Vibert, Nicolas and Nowrouzezahrai, Derek and Hachisuka, Toshiya},
 journal = {{ACM Transactions on Graphics}},
 publisher = {{Association for Computing Machinery}},
 year = {2018},
}
```

Contact
=======

Please feel free to email `adrien.gruson[at]gmail.com` or `binhson.hua[at]gmail.com`  for questions regarding the code. 
