
if [ $# -ne 1 ]
then
    echo "Usage: res_dir"
    exit 1
fi
wd=$1
#"/local/agruson/localImp_2014/localimp_2014_data/scenes/material_scene/references/"

for i in `cat ./data/correspond.txt`
do
	name=`echo $i | cut -d':' -f2`
	num=`echo $i | cut -d':' -f1`
	echo "$num -> $name"
	command="mv $wd$num.hdr $wd$name.hdr"
	eval $command
done
