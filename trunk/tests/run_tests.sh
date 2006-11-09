#!/bin/sh
export FLAGPOLL_PATH=./fpcfiles

for x in `find ./testfiles -name *.test`
do
   source $x
   res=`flagpoll $ARGS`
   if test "$RESULTS" != "$res"
   then
      echo "$x failed, $RESULT is not $res"
   else
      echo "$x passed"
   fi
done

