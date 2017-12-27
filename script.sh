#!/bin/bash

for f in networks/*;
do 
	echo "File $f - "
	echo  "nodes - `grep "</node>" $f | wc -l`"
	echo "links - `grep "</link>" $f | wc -l`"
done
