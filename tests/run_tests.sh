#!/bin/sh
export FLAGPOLL_PATH=./fpcfiles
export FLAGPOLL=../flagpoll

for x in `find ./testfiles -name *.test`
do
   source $x
   res=`$FLAGPOLL $ARGS`
   if test "$RESULTS" != "$res"
   then
      echo "$x failed, '$RESULTS' is not '$res'"
      echo "--------------debug output----------"
      $FLAGPOLL $ARGS --debug
   else
      echo "$x passed"
   fi
done

