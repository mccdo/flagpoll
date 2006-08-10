#    -----------------------------------------------------------------
#
#    Flagpoll: A tool to extract flags from installed applications
#    for compiling, settting variables, etc.
#
#    Original Authors:
#       Daniel E. Shipton <dshipton@gmail.com>
#
#    Flagpoll is Copyright (C) 2006 by Daniel E. Shipton
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to:
#    Free SoftwareFoundation, Inc.
#    51 Franklin Street, Fifth Floor,
#    Boston, MA  02110-1301  USA
#
#    -----------------------------------------------------------------


dnl AM_PATH_FLAGPOLL([MINIMUM-VERSION, [ACTION-IF-FOUND [, ACTION-IF-NOT-FOUND]]])
dnl Test for Flagpoll, and define FLAGPOLL
dnl
AC_DEFUN([AM_PATH_FLAGPOLL],
[
   if test "x$FLAGPOLL" = "x" ; then
     _FLAGPOLL_SETUP()
   fi
])

AC_DEFUN([_FLAGPOLL_SETUP],
[
   AC_ARG_WITH(flagpoll,
            AC_HELP_STRING([--with-flagpoll=PATH],
                        [path where flagpoll is installed (optional)]),
            flagpoll_path="$withval", flagpoll_path="")
   
   if test "x$flagpoll_path" != "x" ; then
      FLAGPOLL=$flagpoll_path
   fi

   AC_PATH_PROG(FLAGPOLL, flagpoll, no)
   min_flagpoll_version=ifelse([$1], ,0.5.0,$1)

   AC_MSG_CHECKING(new for flagpoll version >= $min_flagpoll_version)
   ok=no
   if test "x$FLAGPOLL" != "xno" ; then
      req_major=`echo $min_flagpoll_version | \
               sed 's/\([[0-9]]*\).\([[0-9]]*\).\([[0-9]]*\)/\1/'`
      req_minor=`echo $min_flagpoll_version | \
               sed 's/\([[0-9]]*\).\([[0-9]]*\).\([[0-9]]*\)/\2/'`
      req_micro=`echo $min_flagpoll_version | \
               sed 's/\([[0-9]]*\).\([[0-9]]*\).\([[0-9]]*\)/\3/'`
      flagpoll_version=`$FLAGPOLL --version`
      major=`echo $flagpoll_version | \
               sed 's/\([[0-9]]*\).\([[0-9]]*\).\([[0-9]]*\)/\1/'`
      minor=`echo $flagpoll_version | \
               sed 's/\([[0-9]]*\).\([[0-9]]*\).\([[0-9]]*\)/\2/'`
      micro=`echo $flagpoll_version | \
               sed 's/\([[0-9]]*\).\([[0-9]]*\).\([[0-9]]*\)/\3/'`
      if test "$major" -gt "$req_major"; then
        ok=yes
      else 
        if test "$major" -eq "$req_major"; then
            if test "$minor" -ge "$req_minor"; then
               if test "$micro" -ge "$req_micro"; then
                  ok=yes
               fi
            fi
        fi
      fi
   fi
   
   if test "$ok" = "yes" ; then
      AC_MSG_RESULT(yes (version $flagpoll_version))
      ifelse([$2], , :, [$2])
   else
      AC_MSG_RESULT(no)
      FLAGPOLL=""
      ifelse([$3], , :, [$3])
   fi
   
   AC_SUBST(FLAGPOLL)
])

