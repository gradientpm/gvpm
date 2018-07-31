#!/bin/sh


inputscene="/local/agruson/localImp_2014/localimp_2014_data/scenes/material_scene/bsdf_*.xml"
outputpath="/local/agruson/localImp_2014/localimp_2014_data/scenes/material_scene/test/"
commandbase="python generate_scenes_integrators.py -p rulesLocalImp -o $outputpath "

if [ ! -d $outputpath ]
then
	echo "Create: $outputpath"
	mkdir -p $outputpath
fi

for a in `ls $inputscene`
do
	name=`basename $a`
	name=`echo $name | cut -c6-`
	name=`echo $name | cut -d'.' -f1`
	echo $name
	command="$commandbase -i $a -n bsdf_$name"
	#echo $command
	eval $command
done

# clean up all
techniques="ISPPM LocalImp2D_iteration LocalImp2D_constant_64 LocalImp2D_samples_1M LocalImp3D_constant_64 LocalImp3D_samples_1M"
for t in $techniques
do
	command="rm $outputpath*_$t.xml"
	#echo $command
	eval $command
done
