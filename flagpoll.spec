Summary: Program for retrieving meta-data from installed packages.
Name: flagpoll
Version: 0.1.5
Release: 1
License: GPL
URL: https://realityforge.vrsource.org/view/FlagPoll/WebHome
Group: System Environment/Base
Source: flagpoll-0.1.5.tar.bz2
Requires: python >= 2.3
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

%description
Flagpoll is a program to help obtain options for third party software
useful for compiling a users program.  It also can be used as asystem 
for polling generic meta-data from installed software.

%prep
rm -rf $RPM_BUILD_ROOT
%setup -q
%build

%install
mkdir -p $RPM_BUILD_ROOT/usr
scons prefix=$RPM_BUILD_ROOT/usr install

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{_bindir}/flagpoll
%{_datadir}/flagpoll/flagpoll.fpc
%doc README TODO LICENSE ChangeLog

%changelog
* Wed Jul 05 2006 Daniel E. Shipton <dshipton@infiscape.com> 
- install fpc file and depend on python 2.3
* Fri Jun 30 2006 Daniel E. Shipton <dshipton@infiscape.com> 
- initial specfile
