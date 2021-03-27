#!/bin/bash
# Check for string in file, if not found, backup, then 
# Add the entry

if [ -z "$1" ]
then
   echo "No argument supplied"
   exit 1
fi

FILE=$1
STRING=${@:2}

#echo "Looking in ${FILE} for ${STRING}"
if ! [ -e ${FILE} ]
then
   echo "File ${FILE} does not exist. Exiting"
   exit 0
fi

/bin/grep "$STRING" $FILE
if [ $? -ne 0 ]
then
   echo "$STRING not found in $FILE so appending."
   echo $STRING >> $FILE
else
   echo "${STRING} already found in $FILE Exiting"
   exit 0
fi
