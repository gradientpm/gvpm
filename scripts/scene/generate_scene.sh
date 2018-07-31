#!/usr/bin/env bash
# Usage: "scene dir" "generator" "scene name" "variation xml"

# One argument (xml) is optional
if [ $# -ne 3 -a $# -ne 4 ]; then
    echo "Usage: scene_dir generator scene_name [xml]"
    exit 1
fi

# Get scene directory and generator
WDIR=$1
GENERATOR=$2
if [ ! -d "$WDIR" ]; then
    echo "Scene directory is not found: $WDIR"
    echo "Quit!"
    exit
fi
#TODO: Check the generator location

# Check if the scene dir and scene xml exist
SCENE=$3
totaldir=$WDIR/$SCENE"_scene/"
orifile=$totaldir"ori_$SCENE.xml"
if [ ! -d "$totaldir" ]; then
    echo "[ERROR] No scene dir: $totaldir"
    echo "QUIT"
    exit 1
fi
if [ ! -e "$orifile" ]; then
    echo "[ERROR] No ori scene file: $orifile"
    echo "QUIT"
    exit 1
fi

# Generate scene using the generator
COMM="python generate_scenes_integrators.py -p $GENERATOR -i $orifile -o $totaldir -n $SCENE"
echo $COMM
eval $COMM

# Call variation if option is provided
if [ $# -eq 4 ]
then
    XML=$4
    COMM="python variation_scenes.py -i $totaldir$SCENE -c $XML -r"

    echo $COMM
    eval $COMM
fi
