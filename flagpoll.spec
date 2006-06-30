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
The eject program allows the user to eject removable media
(typically CD-ROMs, floppy disks or Iomega Jaz or Zip disks)
using software control. Eject can also control some multi-
disk CD changers and even some devices' auto-eject features.

Install eject if you'd like to eject removable media using
software control.

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
