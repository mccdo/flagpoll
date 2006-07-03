Summary: Program for retrieving meta-data from installed packages.
Name: flagpoll
Version: 0.1.4
Release: 2
License: GPL
URL: https://realityforge.vrsource.org/view/FlagPoll/WebHome
Group: System Environment/Base
Source: flagpoll-0.1.4.tar.bz2
Requires: python >= 2.4
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
mkdir -p $RPM_BUILD_ROOT/usr/bin
scons prefix=$RPM_BUILD_ROOT/usr install

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{_bindir}/flagpoll
%doc README TODO LICENSE ChangeLog

%changelog
* Fri Jun 30 2006 Daniel E. Shipton <dshipton@infiscape.com> 
- initial specfile
