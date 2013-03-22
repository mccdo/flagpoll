# - a Flagpoll module for CMake, based on CMake's pkg-config module
#
# Usage:
#   flagpoll_check_modules(<PREFIX> [REQUIRED] [QUIET] <MODULE> [<MODULE>]*)
#     checks for all the given modules
#
#   flagpoll_search_module(<PREFIX> [REQUIRED] [QUIET] <MODULE> [<MODULE>]*)
#     checks for given modules and uses the first working one
#
# When the 'REQUIRED' argument was set, macros will fail with an error
# when module(s) could not be found
#
# When the 'QUIET' argument is set, no status messages will be printed.
#
# It sets the following variables:
#   FLAGPOLL_FOUND          ... if flagpoll executable was found
#   FLAGPOLL_EXECUTABLE     ... pathname of the flagpoll program
#   FLAGPOLL_VERSION_STRING ... the version of the flagpoll program found
#
#
# For the following variables two sets of values exist; first one is the
# common one and has the given PREFIX. The second set contains flags
# which are given out when flagpoll was called with the '--static'
# option.
#   <XPREFIX>_FOUND          ... set to 1 if module(s) exist
#   <XPREFIX>_LIBRARIES      ... only the libraries (w/o the '-l')
#   <XPREFIX>_LIBRARY_DIRS   ... the paths of the libraries (w/o the '-L')
#   <XPREFIX>_LDFLAGS        ... all required linker flags
#   <XPREFIX>_LDFLAGS_OTHER  ... all other linker flags
#   <XPREFIX>_INCLUDE_DIRS   ... the '-I' preprocessor flags (w/o the '-I')
#   <XPREFIX>_CFLAGS         ... all required cflags
#   <XPREFIX>_CFLAGS_OTHER   ... the other compiler flags
#
#   <XPREFIX> = <PREFIX>        for common case
#   <XPREFIX> = <PREFIX>_STATIC for static linking
#
# There are some special variables whose prefix depends on the count
# of given modules. When there is only one module, <PREFIX> stays
# unchanged. When there are multiple modules, the prefix will be
# changed to <PREFIX>_<MODNAME>:
#   <XPREFIX>_VERSION    ... version of the module
#   <XPREFIX>_PREFIX     ... prefix-directory of the module
#   <XPREFIX>_INCLUDEDIR ... include-dir of the module
#   <XPREFIX>_LIBDIR     ... lib-dir of the module
#
#   <XPREFIX> = <PREFIX>  when |MODULES| == 1, else
#   <XPREFIX> = <PREFIX>_<MODNAME>
#
# A <MODULE> parameter can have the following formats:
#   {MODNAME}            ... matches any version
#   {MODNAME}>={VERSION} ... at least version <VERSION> is required
#   {MODNAME}={VERSION}  ... exactly version <VERSION> is required
#   {MODNAME}<={VERSION} ... modules must not be newer than <VERSION>
#
# Examples
#   flagpoll_check_modules (GLIB2   glib-2.0)
#
#   flagpoll_check_modules (GLIB2   glib-2.0>=2.10)
#     requires at least version 2.10 of glib2 and defines e.g.
#       GLIB2_VERSION=2.10.3
#
#   flagpoll_check_modules (FOO     glib-2.0>=2.10 gtk+-2.0)
#     requires both glib2 and gtk2, and defines e.g.
#       FOO_glib-2.0_VERSION=2.10.3
#       FOO_gtk+-2.0_VERSION=2.8.20
#
#   flagpoll_check_modules (XRENDER REQUIRED xrender)
#     defines e.g.:
#       XRENDER_LIBRARIES=Xrender;X11
#       XRENDER_STATIC_LIBRARIES=Xrender;X11;pthread;Xau;Xdmcp
#
#   flagpoll_search_module (BAR     libxml-2.0 libxml2 libxml>=2)

# we use string( FIND ... ), so we need at least 2.8.5
cmake_minimum_required( VERSION 2.8.5 )

set( FLAGPOLL_VERSION 1 )

find_program( FLAGPOLL_EXECUTABLE NAMES flagpoll DOC "flagpoll executable" )
mark_as_advanced( FLAGPOLL_EXECUTABLE )

if( FLAGPOLL_EXECUTABLE )
    execute_process( COMMAND ${FLAGPOLL_EXECUTABLE} --version
                     OUTPUT_VARIABLE FLAGPOLL_VERSION_STRING
                     ERROR_QUIET
                     OUTPUT_STRIP_TRAILING_WHITESPACE )
endif()

include( FindPackageHandleStandardArgs )
find_package_handle_standard_args( Flagpoll
                                   REQUIRED_VARS FLAGPOLL_EXECUTABLE
                                   VERSION_VAR FLAGPOLL_VERSION_STRING )

macro( _flagpoll_unset var )
    set( ${var} "" CACHE INTERNAL "" )
endmacro()

macro( _flagpoll_set var value )
    set( ${var} ${value} CACHE INTERNAL "" )
endmacro()

# invokes flagpoll, cleans up the results and sets variables
macro( _flagpoll_invoke _pkg _prefix _varname _regexp )
    set( _flagpoll_invoke_result )

    execute_process( COMMAND ${FLAGPOLL_EXECUTABLE} ${_pkg} --no-deps ${ARGN}
                     OUTPUT_VARIABLE _flagpoll_invoke_result
                     RESULT_VARIABLE _flagpoll_failed )

    if( _flagpoll_failed )
        set( _flagpoll_${_varname} "" )
        _flagpoll_unset( ${_prefix}_${_varname} )
    else()
        string( REGEX REPLACE "[\r\n]" " " _flagpoll_invoke_result "${_flagpoll_invoke_result}" )
        string( REGEX REPLACE " +$" "" _flagpoll_invoke_result "${_flagpoll_invoke_result}" )

        if( NOT "${_flagpoll_invoke_result}" STREQUAL "" )
            string( FIND ${_flagpoll_invoke_result} "\\" _result_has_backslash )
            if( NOT ${_result_has_backslash} EQUAL -1 )
                file( TO_CMAKE_PATH ${_flagpoll_invoke_result} _flagpoll_invoke_result )
            endif()
        endif()

        if( NOT ${_regexp} STREQUAL "" )
            string( REGEX REPLACE "${_regexp}" " " _flagpoll_invoke_result "${_flagpoll_invoke_result}" )
        endif()

        separate_arguments( _flagpoll_invoke_result )

        set( _flagpoll_${_varname} ${_flagpoll_invoke_result} )
        _flagpoll_set( ${_prefix}_${_varname} "${_flagpoll_invoke_result}" )
    endif()
endmacro()

# Invokes flagpoll two times; once without '--static' and once with '--static'
macro( _flagpoll_invoke_dyn _pkg _prefix _varname _cleanup_regexp )
    _flagpoll_invoke( "${_pkg}" ${_prefix} ${_varname} "${_cleanup_regexp}" ${ARGN} )
    _flagpoll_invoke( "${_pkg}" ${_prefix} STATIC_${_varname} "${_cleanup_regexp}" --static ${ARGN} )
endmacro()

# Splits given arguments into options and a package list
macro( _flagpoll_parse_options _result _is_required _is_silent )
    set( ${_is_required} 0 )
    set( ${_is_silent} 0 )

    foreach( _pkg ${ARGN} )
        if( _pkg STREQUAL "REQUIRED" )
            set( ${_is_required} 1 )
        endif()

        if( _pkg STREQUAL "QUIET" )
            set( ${_is_silent} 1 )
        endif()
    endforeach()

    set( ${_result} ${ARGN} )
    list( REMOVE_ITEM ${_result} "REQUIRED" )
    list( REMOVE_ITEM ${_result} "QUIET" )
endmacro()

macro( _flagpoll_check_modules_internal _is_required _is_silent _prefix )
    _flagpoll_unset( ${_prefix}_FOUND )
    _flagpoll_unset( ${_prefix}_VERSION )
    _flagpoll_unset( ${_prefix}_PREFIX )
    _flagpoll_unset( ${_prefix}_INCLUDEDIR )
    _flagpoll_unset( ${_prefix}_LIBDIR )
    _flagpoll_unset( ${_prefix}_LIBS )
    _flagpoll_unset( ${_prefix}_LIBS_L )
    _flagpoll_unset( ${_prefix}_LIBS_PATHS )
    _flagpoll_unset( ${_prefix}_LIBS_OTHER )
    _flagpoll_unset( ${_prefix}_CFLAGS )
    _flagpoll_unset( ${_prefix}_CFLAGS_I )
    _flagpoll_unset( ${_prefix}_CFLAGS_OTHER )
    _flagpoll_unset( ${_prefix}_STATIC_LIBDIR )
    _flagpoll_unset( ${_prefix}_STATIC_LIBS )
    _flagpoll_unset( ${_prefix}_STATIC_LIBS_L )
    _flagpoll_unset( ${_prefix}_STATIC_LIBS_PATHS )
    _flagpoll_unset( ${_prefix}_STATIC_LIBS_OTHER )
    _flagpoll_unset( ${_prefix}_STATIC_CFLAGS )
    _flagpoll_unset( ${_prefix}_STATIC_CFLAGS_I )
    _flagpoll_unset( ${_prefix}_STATIC_CFLAGS_OTHER )

    # create a better addressable variable of the modules and calculate its size
    set( _flagpoll_check_modules_list ${ARGN} )
    list( LENGTH _flagpoll_check_modules_list _flagpoll_check_modules_cnt )

    if( FLAGPOLL_EXECUTABLE )
        # give out status message telling checked module
        if( NOT ${_is_silent} )
            if( _flagpoll_check_modules_cnt EQUAL 1 )
                message( STATUS "checking for module '${_flagpoll_check_modules_list}'" )
            else()
                message( STATUS "checking for modules '${_flagpoll_check_modules_list}'" )
            endif()
        endif()

        set( _flagpoll_check_modules_packages )
        set( _flgapoll_check_modules_failed )

        # iterate through module list and check whether they exist and match the required version
        foreach( _flagpoll_check_modules_pkg ${_flagpoll_check_modules_list} )
            set( _flagpoll_check_modules_exist_query )

            # check whether version is given
            if ( _flagpoll_check_modules_pkg MATCHES ".*(>=|=|<=).*" )
                string( REGEX REPLACE "(.*[^><])(>=|=|<=)(.*)" "\\1" _flagpoll_check_modules_pkg_name "${_flagpoll_check_modules_pkg}" )
                string( REGEX REPLACE "(.*[^><])(>=|=|<=)(.*)" "\\2" _flagpoll_check_modules_pkg_op   "${_flagpoll_check_modules_pkg}" )
                string( REGEX REPLACE "(.*[^><])(>=|=|<=)(.*)" "\\3" _flagpoll_check_modules_pkg_ver  "${_flagpoll_check_modules_pkg}" )
            else()
                set( _flagpoll_check_modules_pkg_name "${_flagpoll_check_modules_pkg}" )
                set( _flagpoll_check_modules_pkg_op )
                set( _flagpoll_check_modules_pkg_ver )
            endif()

            # handle the operands and create the final query which is of the format:
            # * <pkg-name> --atleast-version=<version>
            # * <pkg-name> --exact-version=<version>
            # * <pkg-name> --max-release=<version>
            # * <pkg-name> --exists
            if( _flagpoll_check_modules_pkg_op STREQUAL ">=" )
                list( APPEND _flagpoll_check_modules_exist_query --atleast-version=${_flagpoll_check_modules_pkg_ver} )
            endif()

            if( _flagpoll_check_modules_pkg_op STREQUAL "=" )
                list( APPEND _flagpoll_check_modules_exist_query --exact-version=${_flagpoll_check_modules_pkg_ver} )
            endif()

            if( _flagpoll_check_modules_pkg_op STREQUAL "<=" )
                list (APPEND _flagpoll_check_modules_exist_query --max-release=${_flagpoll_check_modules_pkg_ver} )
            endif()

            if( NOT _flagpoll_check_modules_pkg_op )
                list( APPEND _flagpoll_check_modules_exist_query --exists )
            endif()

            _flagpoll_unset( ${_prefix}_${_flagpoll_check_modules_pkg_name}_VERSION )
            _flagpoll_unset( ${_prefix}_${_flagpoll_check_modules_pkg_name}_PREFIX )
            _flagpoll_unset( ${_prefix}_${_flagpoll_check_modules_pkg_name}_INCLUDEDIR )
            _flagpoll_unset( ${_prefix}_${_flagpoll_check_modules_pkg_name}_LIBDIR )

            list( APPEND _flagpoll_check_modules_packages "${_flagpoll_check_modules_pkg_name}" )

            # execute the query
            execute_process( COMMAND ${FLAGPOLL_EXECUTABLE} ${_flagpoll_check_modules_pkg_name} ${_flagpoll_check_modules_exist_query}
                             RESULT_VARIABLE _flagpoll_retval
                             OUTPUT_QUIET )

            # evaluate result and tell failures
            if( _flagpoll_retval )
                if( NOT ${_is_silent} )
                    message( STATUS "  package '${_flagpoll_check_modules_pkg}' not found" )
                endif()

                set( _flagpoll_check_modules_failed 1 )
            endif()
        endforeach()

        if( _flagpoll_check_modules_failed )
            # fail when requested
            if( ${_is_required} )
                message( SEND_ERROR "A required package was not found" )
            endif()
        else()
            # when we are here, we checked whether requested modules
            # exist. Now, go through them and set variables

            _flagpoll_set( ${_prefix}_FOUND 1 )
            list( LENGTH _flagpoll_check_modules_packages pkg_count )

            # iterate through all modules again and set individual variables
            foreach( _flagpoll_check_modules_pkg ${_flagpoll_check_modules_packages} )
                # handle case when there is only one package required
                if( pkg_count EQUAL 1 )
                    set( _flagpoll_check_prefix "${_prefix}" )
                else()
                    set( _flagpoll_check_prefix "${_prefix}_${_flagpoll_check_modules_pkg}" )
                endif()

                _flagpoll_invoke( ${_flagpoll_check_modules_pkg} "${_flagpoll_check_prefix}" VERSION    ""   --modversion )
                _flagpoll_invoke( ${_flagpoll_check_modules_pkg} "${_flagpoll_check_prefix}" PREFIX     ""   --variable=prefix )
                _flagpoll_invoke( ${_flagpoll_check_modules_pkg} "${_flagpoll_check_prefix}" INCLUDEDIR ""   --variable=includedir )
                _flagpoll_invoke( ${_flagpoll_check_modules_pkg} "${_flagpoll_check_prefix}" LIBDIR     ""   --variable=libdir )

                if( NOT ${_is_silent} )
                    message( STATUS "  found ${_flagpoll_check_modules_pkg}, version ${_flagpoll_VERSION}" )
                endif()

                # set variables
                if( MSVC )
                    _flagpoll_invoke_dyn( "${_flagpoll_check_modules_pkg}" "${_flagpoll_check_prefix}" LIBRARIES "" --libs-only-l ) 
                    _flagpoll_invoke_dyn( "${_flagpoll_check_modules_pkg}" "${_flagpoll_check_prefix}" LIBRARY_DIRS "(^| )/libpath:|[\"]" --libs-only-L )
                else()
                    _flagpoll_invoke_dyn( "${_flagpoll_check_modules_pkg}" "${_flagpoll_check_prefix}" LIBRARIES "(^| )-l" --libs-only-l )
                    _flagpoll_invoke_dyn( "${_flagpoll_check_modules_pkg}" "${_flagpoll_check_prefix}" LIBRARY_DIRS "(^| )-L" --libs-only-L )
                endif()

                _flagpoll_invoke_dyn( "${_flagpoll_check_modules_pkg}" "${_flagpoll_check_prefix}" LDFLAGS "" --libs )
                _flagpoll_invoke_dyn( "${_flagpoll_check_modules_pkg}" "${_flagpoll_check_prefix}" LDFLAGS_OTHER "" --libs-only-other )

                if( MSVC )
                    _flagpoll_invoke_dyn( "${_flagpoll_check_modules_pkg}" "${_flagpoll_check_prefix}" INCLUDE_DIRS "(^| )/I|(^| )-I|[\"]" --cflags-only-I )
                else()
                    _flagpoll_invoke_dyn( "${_flagpoll_check_modules_pkg}" "${_flagpoll_check_prefix}" INCLUDE_DIRS "(^| )-I" --cflags-only-I )
                endif()

                _flagpoll_invoke_dyn( "${_flagpoll_check_modules_pkg}" "${_flagpoll_check_prefix}" CFLAGS "" --cflags )
                _flagpoll_invoke_dyn( "${_flagpoll_check_modules_pkg}" "${_flagpoll_check_prefix}" CFLAGS_OTHER "" --cflags-only-other )
            endforeach()
        endif()
    else()
        if( ${_is_required} )
            message( SEND_ERROR "flagpoll tool not found" )
        endif()
    endif()
endmacro()

###
### User visible macros
###

macro( flagpoll_check_modules _prefix _module0 )
    # check cached value
    if( NOT DEFINED __flagpoll_checked_${_prefix}
        OR __flagpoll_checked_${_prefix} LESS ${FLAGPOLL_VERSION}
        OR NOT ${_prefix}_FOUND )

        _flagpoll_parse_options( _pkg_modules _pkg_is_required _pkg_is_silent "${_module0}" ${ARGN} )
        _flagpoll_check_modules_internal( "${_pkg_is_required}" "${_pkg_is_silent}" "${_prefix}" ${_pkg_modules} )

        _flagpoll_set(__flagpoll_checked_${_prefix} ${FLAGPOLL_VERSION} )
    endif()
endmacro()

macro( flagpoll_search_module _prefix _module0 )
    # check cached value
    if ( NOT DEFINED __flagpoll_checked_${_prefix}
        OR __flagpoll_checked_${_prefix} LESS ${FLAGPOLL_VERSION}
        OR NOT ${_prefix}_FOUND )

        set( _pkg_modules_found 0 )
        _flagpoll_parse_options( _pkg_modules_alt _pkg_is_required _pkg_is_silent "${_module0}" ${ARGN} )

        if( NOT ${_pkg_is_silent} )
            message( STATUS "checking for one of the modules '${_pkg_modules_alt}'" )
        endif ()

        # iterate through all modules and stop at the first working one.
        foreach( _pkg_alt ${_pkg_modules_alt} )
            if( NOT _pkg_modules_found )
                _flagpoll_check_modules_internal( 0 1 "${_prefix}" "${_pkg_alt}" )
            endif()

            if( ${_prefix}_FOUND )
                set( _pkg_modules_found 1 )
            endif()
        endforeach()

        if( NOT ${_prefix}_FOUND )
            if( ${_pkg_is_required} )
                message( SEND_ERROR "None of the required '${_pkg_modules_alt}' found" )
            endif()
        endif()

        _flagpoll_set(__flagpoll_checked_${_prefix} ${FLAGPOLL_VERSION} )
    endif()
endmacro()
