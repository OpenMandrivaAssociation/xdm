%define	with_consolekit	1
Name: xdm
Version: 1.1.6
Release: %mkrel 6
Summary: X Display Manager with support for XDMCP 
Group: System/X11
URL: http://xorg.freedesktop.org
Source: http://xorg.freedesktop.org/releases/individual/app/%{name}-%{version}.tar.bz2
Source1: xdm.pamd
License: MIT
BuildRoot: %{_tmppath}/%{name}-root

BuildRequires: libx11-devel >= 1.0.0
BuildRequires: libxau-devel >= 1.0.0
BuildRequires: libxdmcp-devel >= 1.0.0
BuildRequires: libxmu-devel >= 1.0.0
BuildRequires: libxt-devel >= 1.0.0
BuildRequires: libxaw-devel >= 1.0.1
BuildRequires: x11-util-macros >= 1.0.1
BuildRequires: libpam-devel
%if %{with_consolekit}
BuildRequires:	consolekit-devel
BuildRequires:	libdbus-devel
%endif
Requires: xinitrc xrdb
Requires: sessreg
Conflicts: xorg-x11 < 7.0

Patch1: 0001-Restore-endif-accidentally-removed-in-d0d4581be22ab.patch
Patch2: 0002-Debian-bug-440389-800x600-settings-got-lost-scree.patch
Patch3: 0003-Darwin-doesn-t-need-__DARWIN__-anymore.patch
Patch4: 0004-Support-kdm-extended-syntax-to-reserve-a-server-for.patch
Patch5: 0005-Initialize-the-greeter-only-after-checking-if-the-th.patch
Patch6: 0006-Ass-console-kit-support-to-xdm.patch
Patch7: 0007-Add-files-required-by-consolekit-support.patch

%description
Xdm manages a collection of X displays, which may be on the local host or
remote servers. The design of xdm was guided by the needs of X terminals as
well as The Open Group standard XDMCP, the X Display Manager Control Protocol.
Xdm provides services similar to those provided by init, getty and login on
character terminals: prompting for login name and password, authenticating the
user, and running a session.

%prep
%setup -q -n %{name}-%{version}

%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1

%build
%configure2_5x	--x-includes=%{_includedir}\
		--x-libraries=%{_libdir} \
		%if %{with_consolekit}
		--with-consolekit \
		%endif
		--with-pam

%make

%install
rm -rf %{buildroot}
%makeinstall_std

LC_ALL=C
LANG=C
export LC_ALL LANG

# remove files that are in xinitrc
rm -rf %{buildroot}%{_libdir}/X11/xdm/{[A-Z]*,xdm-config}

ln -s ../../../../etc/X11/xdm/xdm-config %{buildroot}%{_libdir}/X11/xdm

# remove unused devel files
rm -rf %{buildroot}%{_libdir}/X11/xdm/*.{a,la}

# install PAM file
mkdir -p %{buildroot}%{_sysconfdir}/pam.d
install -m 644 %{_sourcedir}/xdm.pamd $RPM_BUILD_ROOT/etc/pam.d/xdm

install -d $RPM_BUILD_ROOT/var/lib/xdm
ln -sf ../../../../var/lib/xdm %{buildroot}%{_libdir}/X11/xdm/authdir

# logrotate
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
cat << EOF > %{buildroot}%{_sysconfdir}/logrotate.d/xdm
/var/log/xdm-error.log {
    notifempty
    missingok
    nocompress
}
EOF

%pre
if [ -d %{_libdir}/X11/xdm/authdir ]; then
	# this is now a symlink
	rm -rf %{_libdir}/X11/xdm/authdir
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/pam.d/xdm
%config(noreplace) %{_sysconfdir}/logrotate.d/xdm
%dir /var/lib/xdm
%{_bindir}/xdm
%{_bindir}/xdmshell
%{_datadir}/X11/app-defaults/Chooser
%{_mandir}/man1/xdm.*
%{_libdir}/X11/xdm/*
