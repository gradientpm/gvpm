#!/usr/bin/env bash
# Usage: "Scene dir" scene1 scene2 scene3 scene4 [...]
WDIR=$1

# Test that the working directory exists or not
if [ ! -d "$WDIR" ]; then
    echo "No Working directory found: $WDIR"
    echo "Quit"
    exit
fi

# Create the scenes vectors
nbscenes=$(($#-1))
echo "Number scenes: $nbscenes"

scenes="$2"
for i in $(eval echo {3..$#})
do
    sceneName=$(eval echo \$$i)
    scenes=$scenes" "$sceneName
done
echo "Scenes: $scenes"

# Remove all generated files
for s in $scenes
do
	totaldir=$WDIR$s"_scene/"
	if [ -d "$totaldir" ]; then
		search=$totaldir$s"_*.xml"
		ls $search
		rm -v $search
	fi
done