#!/usr/bin/env bash
OUT_PATH="/udd/agruson/maxRef/ref_"
SCENE_PATH="/temp_dd/igrida-fs1/agruson/data2/scenes/"
TEMP_DIR="ref_out/"

# runComputation(sceneName, resX, resY, blockSize)
runComputation() {
    sceneName=$1
    resX=$2
    resY=$3
    blockSize=$4

    # Concat names
    OUTHDR=$OUT_PATH$sceneName".hdr"
    TMPDIR=$SCENE_PATH$sceneName"_scene/"$TEMP_DIR
    XMLSCENE=$SCENE_PATH$sceneName"_scene/ref_"$sceneName".xml"
    
    # Test if the xml exist or not
	COMMANDCONTACT="python igridaResults.py -x "$resX" -y "$resY" -b "$blockSize" -1 -o "$OUTHDR" -i "$TMPDIR

	echo $COMMANDCONTACT
	eval $COMMANDCONTACT
}  

runComputation "bathroom" 1280 720 32
runComputation "bookshelf" 1280 720 32
runComputation "bottle" 1280 720 32
runComputation "cbox" 512 512 64
runComputation "kitchen" 1280 720 32
# PMBox
runComputation "sponza" 1280 720 64
runComputation "veach-door" 1280 720 32
runComputation "veach-lamp" 1024 576 32
# Villa


