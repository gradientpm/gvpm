#include "../shift_utilities.h"
#include "../../gvpm_beams.h"

#ifndef MITSUBA_SHIFT_DIFFUSE_H
#define MITSUBA_SHIFT_DIFFUSE_H

MTS_NAMESPACE_BEGIN

class BeamGradRadianceQuery;

bool diffuseReconnection(ShiftRecord &sRec, const Intersection &newIts,
                         const Vector &newD, Float newDLength,
                         const PathVertex *parentVertex,
                         const PathEdge *edge, bool isVolumeBase,
                         const Point &predPos, bool adjointCorr = false);

bool diffuseReconnectionPhotonBeam(ShiftRecord &sRec, const Point &newPos, const Point &basePos,
                                   const Vector &newD, Float newDLength,
                                   const PathVertex *baseVertex,
                                   const PathVertex *parentVertex,
                                   const PathEdge *parentEdge, Float pdfEdgeFailed,
                                   bool longBeam, const Point &parentParentPos, bool adjointCorr = false);

MTS_NAMESPACE_END

#endif //MITSUBA_SHIFT_DIFFUSE_H
