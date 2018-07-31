OUT_PATH="/udd/agruson/ref_"
SCENE_PATH="/temp_dd/igrida-fs1/agruson/data/scenes/"
TEMP_DIR="ref_out2/"

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
    if [ -f "$XMLSCENE" ]
    then
        COMMAND="python makeImageIgrida.py -x "$resX" -y "$resY" -i "$XMLSCENE" -e hdr -o "$TMPDIR" -a BEST -t 1:0:0 -j 4 -s "$blockSize
	COMMANDCONTACT="python igridaResults.py -x "$resX" -y "$resY" -b "$blockSize" -1 -o "$OUTHDR" -i "$TMPDIR

	echo $COMMAND
	eval $COMMAND

	echo $COMMANDCONTACT
	eval $COMMANDCONTACT
    else
	echo "File $XMLSCENE NOT FOUND, avoid computation"
    fi
}  

#runComputation "bathroom" 1280 720 32
#runComputation "bookshelf" 1280 720 32
#runComputation "bottle" 1280 720 32
#runComputation "cbox" 512 512 64
#runComputation "kitchen" 1280 720 32
# PMBox
#runComputation "sponza" 1280 720 64
#runComputation "veach-door" 1280 720 32
#runComputation "veach-lamp" 1024 576 32
# Villa


