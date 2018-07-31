#!/bin/sh
#OAR -l core=1,walltime=00:05:00
#OAR --array-param-file /temp_dd/igrida-fs1/agruson/igridaRooms/outHachiNew/argshachi_c9.txt
#OAR -O /temp_dd/igrida-fs1/agruson/igridaRooms/outHachiNew/hachi_c9.out
#OAR -E /temp_dd/igrida-fs1/agruson/igridaRooms/outHachiNew/hachi_c9.err
set -xv

EXECUTABLE=/temp_dd/igrida-fs1/agruson/mtsbin_multi/mitsuba.sh

echo
echo "=============== RUN ==============="
echo "Running ..."
$EXECUTABLE $*
echo "Done"
echo "==================================="