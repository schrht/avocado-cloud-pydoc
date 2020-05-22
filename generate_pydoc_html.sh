#!/usr/bin/env bash

# Description:
#   Create HTML pydoc for avocado_cloud test cases.
#   Run this script under avocado-cloud/tests/.
#
# History:
#   v1.0  2020-05-20  charles.shih  init version

output_path=pydoc-html

# prase the inputs
if [ -z "$1" ]; then
	echo "Usage: $0 <project>"
	exit 1
elif [ ! -d "$1" ]; then
	echo "Error: directory $1 cannot be found."
	exit 1
else
	project=$1
fi

# get modules (.py files)
pyfiles=$(find $project -name '*.py')

mkdir -p $output_path/$project
cp $pyfiles $output_path/$project

# remove inheritance
sed -i '/^from .* import/d' $output_path/$project/*.py
sed -i '/^import /d' $output_path/$project/*.py
sed -i 's/\(^class .*\)(Test):/\1():/' $output_path/$project/*.py

# generate html pages
cd $output_path

for item in $(echo $pyfiles); do
    pydoc -w $(echo $item | tr '/' '.' | sed 's/.py$//')
done
pydoc -w $project

cat ./$project/*.py > ${project}-flat.py
pydoc -w ${project}-flat

# demo
echo ""
echo "Review the pydoc in html:"
echo "firefox $output_path/$project.html"
echo "firefox $output_path/${project}-flat.html"

exit 0

