%define	with_consolekit	1
%define xdm_libdir	%{_datadir}/X11/xdm
Name: xdm
Version: 1.1.8
Release: %mkrel 5
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
Requires: xinitrc > 2.4.19-9
Requires: xrdb
Requires: sessreg
Conflicts: xorg-x11 < 7.0

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
		--with-xdmlibdir=%{xdm_libdir} \
		--with-pam

%make

%install
rm -rf %{buildroot}
%makeinstall_std

LC_ALL=C
LANG=C
export LC_ALL LANG

# remove files that are in xinitrc
rm -rf %{buildroot}%{xdm_libdir}/{[A-Z]*,xdm-config}

# remove unused devel files
rm -rf %{buildroot}%{xdm_libdir}/*.{a,la}

# install PAM file
mkdir -p %{buildroot}%{_sysconfdir}/pam.d
install -m 644 %{_sourcedir}/xdm.pamd $RPM_BUILD_ROOT/etc/pam.d/xdm

install -d %{buildroot}/var/lib/xdm
ln -sf /var/lib/xdm %{buildroot}%{xdm_libdir}/authdir

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
if [ -d %{xdm_libdir}/authdir ]; then
	# this is now a symlink
	rm -rf %{xdm_libdir}/authdir
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
%{_mandir}/man1/xdm.*
%{xdm_libdir}/*
%{_datadir}/X11/app-defaults/Chooser
