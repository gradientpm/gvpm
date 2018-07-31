# Integrators
if (NOT MTS_VERSION)
  message(FATAL_ERROR "Use the top level configuration file")
endif()

macro(add_integrator)
  add_mts_plugin(${ARGN} TYPE integrator)
endmacro()

macro(add_bidir)
  add_integrator(${ARGN} MTS_BIDIR)
endmacro()

if (MTS_CUDA)
    list(APPEND CUDA_NVCC_FLAGS "-arch=sm_52;-std=c++11")
    SET(CUDA_PROPAGATE_HOST_FLAGS OFF)
    INCLUDE_DIRECTORIES(${CUDA_INCLUDE_DIRS})
    macro(add_recons)
        add_mtsCUDA_plugin(${ARGN} MTS_BIDIR TYPE integrator)
    endmacro()
    SET(RECONSFILE poisson_solver/BackendCUDA.cu)
else()
    macro(add_recons)
        add_bidir(${ARGN})
    endmacro()
    SET(RECONSFILE poisson_solver/BackendOpenMP.cpp)
endif()

add_integrator(ao       direct/ao.cpp)
add_integrator(direct   direct/direct.cpp)
add_integrator(path     path/path.cpp)
add_integrator(path_sppm     path/path_sppm.cpp)
add_integrator(path_missing     path/path_missing.cpp)
add_integrator(path_local     path/path_localFrame.cpp)
add_integrator(volpath  path/volpath.cpp)
add_integrator(volpath_simple path/volpath_simple.cpp)
add_integrator(ptracer  ptracer/ptracer.cpp
                        ptracer/ptracer_proc.h ptracer/ptracer_proc.cpp)

# Photon mapping-based techniques
add_integrator(photonmapper photonmapper/photonmapper.cpp photonmapper/bre.cpp)
add_integrator(ppm          photonmapper/ppm.cpp)
add_integrator(sppm         photonmapper/sppm.cpp
        photonmapper/bre.cpp
        photonmapper/photon_proc.cpp

        photonmapper/beams.cpp
        photonmapper/beams_accel.h
        photonmapper/beams_accel.cpp
        photonmapper/beams_struct.h

        photonmapper/plane_struct.h
        photonmapper/plane_accel.h
        photonmapper/plane_accel.cpp

        # Helpers
        volume_utils.h
        )

# Miscellaneous
add_integrator(vpl          vpl/vpl.cpp MTS_HW)
add_integrator(adaptive     misc/adaptive.cpp)
add_integrator(irrcache     misc/irrcache.cpp
                            misc/irrcache_proc.h misc/irrcache_proc.cpp)
add_integrator(multichannel misc/multichannel.cpp)
add_integrator(field        misc/field.cpp)

# Average rendering integrator (for pt, bdpt, ...)
add_integrator(avg        avg.cpp)


# Bidirectional techniques
add_bidir(bdpt          bdpt/bdpt.h      bdpt/bdpt.cpp
                        bdpt/bdpt_proc.h bdpt/bdpt_proc.cpp
                        bdpt/bdpt_wr.h   bdpt/bdpt_wr.cpp)

add_bidir(pssmlt        pssmlt/pssmlt.h         pssmlt/pssmlt.cpp
                        pssmlt/pssmlt_proc.h    pssmlt/pssmlt_proc.cpp
                        pssmlt/pssmlt_sampler.h pssmlt/pssmlt_sampler.cpp)

add_bidir(mlt           mlt/mlt.h      mlt/mlt.cpp
                        mlt/mlt_proc.h mlt/mlt_proc.cpp)

add_bidir(erpt          erpt/erpt.h      erpt/erpt.cpp
                        erpt/erpt_proc.h erpt/erpt_proc.cpp)

# Gradiants techniques
#set_source_files_properties(gpt/gpt.cpp PROPERTIES COMPILE_FLAGS -fpermissive) #TODO
add_recons(gpt      gpt/gpt.cpp   gpt/gpt_wr.cpp
                    gpt/gpt_proc.cpp

                    poisson_solver/Solver.cpp
                    poisson_solver/Backend.cpp
                    ${RECONSFILE}
                    poisson_solver/Defs.cpp)
add_recons(gbdpt        gbdpt/gbdpt.cpp       gbdpt/gbdpt.h
                        gbdpt/gbdpt_proc.cpp  gbdpt/gbdpt_proc.h
                        gbdpt/gbdpt_wr.cpp    gbdpt/gbdpt_wr.h

                        poisson_solver/Solver.cpp
                        poisson_solver/Backend.cpp
                        ${RECONSFILE}
                        poisson_solver/Defs.cpp)

add_recons(gvpm        photonmapper/gvpm/gvpm.cpp
        photonmapper/gvpm/gvpm_proc.cpp
        photonmapper/gvpm/gvpm_accel.cpp
        photonmapper/gvpm/gvpm_gatherpoint.h
        photonmapper/gvpm/gvpm_struct.h

        poisson_solver/Solver.cpp
        poisson_solver/Backend.cpp
        ${RECONSFILE}
        poisson_solver/Defs.cpp

        # Helpers
        volume_utils.h
        photonmapper/gvpm/gvpm_geoOps.h

        # Beam-beam implementation
        photonmapper/beams.cpp
        photonmapper/beams_accel.cpp
        photonmapper/beams_struct.h
        photonmapper/gvpm/gvpm_beams.h

        # Photon plane implementation
        photonmapper/plane_struct.h
        photonmapper/plane_accel.h
        photonmapper/plane_accel.cpp
        photonmapper/gvpm/gvpm_plane.h

        # Shifts
        photonmapper/gvpm/shift/shift_surface.cpp
        photonmapper/gvpm/shift/shift_volume_photon.cpp
        photonmapper/gvpm/shift/shift_volume_beams.cpp
        photonmapper/gvpm/shift/shift_volume_planes.h
        photonmapper/gvpm/shift/shift_utilities.h

        # Special shift
        photonmapper/gvpm/shift/operation/shift_ME.cpp
        photonmapper/gvpm/shift/operation/shift_diffuse.h
        photonmapper/gvpm/shift/operation/shift_diffuse.cpp
        photonmapper/gvpm/shift/operation/shift_medium.h


        )