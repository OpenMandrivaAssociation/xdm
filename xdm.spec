%define xdm_libdir %{_datadir}/X11/xdm

Name:		xdm
Version:	1.1.12
Release:	1
Summary:	X Display Manager with support for XDMCP
Group:		System/X11
License:	MIT
URL:		http://xorg.freedesktop.org
Source0:	http://xorg.freedesktop.org/releases/individual/app/%{name}-%{version}.tar.bz2
Source1:	xdm.pamd
Patch4:		0004-Support-kdm-extended-syntax-to-reserve-a-server-for.patch
#Patch5: 0005-Initialize-the-greeter-only-after-checking-if-the-th.patch
Patch8:		xdm-1.1.11-fix-service-file.patch
BuildRequires:	pkgconfig(x11) >= 1.0.0
BuildRequires:	pkgconfig(xau) >= 1.0.0
BuildRequires:	pkgconfig(xaw7) >= 1.0.1
BuildRequires:	pkgconfig(xdmcp) >= 1.0.0
BuildRequires:	pkgconfig(xmu) >= 1.0.0
BuildRequires:	pkgconfig(xorg-macros) >= 1.3.0
BuildRequires:	pkgconfig(xt) >= 1.0.0
BuildRequires:	pam-devel
BuildRequires:	systemd-macros
BuildRequires: rpm-helper
Requires:	xinitrc > 2.4.19-9
Requires:	xrdb
Requires:	sessreg
Conflicts:	xorg-x11 < 7.0
Requires(post,postun,preun): rpm-helper

%description
Xdm manages a collection of X displays, which may be on the local host or
remote servers. The design of xdm was guided by the needs of X terminals as
well as The Open Group standard XDMCP, the X Display Manager Control Protocol.
Xdm provides services similar to those provided by init, getty and login on
character terminals: prompting for login name and password, authenticating the
user, and running a session.

%prep
%autosetup -p1

%build
%configure \
    --x-includes=%{_includedir}\
    --x-libraries=%{_libdir} \
    --with-xdmlibdir=%{xdm_libdir} \
    --with-pam \
    --with-systemdsystemunitdir=%{_unitdir} \
    --enable-xdmshell

%make_build

%install
%make_install

LC_ALL=C
LANG=C
export LC_ALL LANG

# remove files that are in xinitrc
rm -rf %{buildroot}%{xdm_libdir}/{[A-Z]*,xdm-config}

# remove unused devel files
rm -rf %{buildroot}%{xdm_libdir}/*.{a,la}

# install PAM file
mkdir -p %{buildroot}%{_sysconfdir}/pam.d
install -m 644 %{SOURCE1} %{buildroot}/etc/pam.d/xdm

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

%files
%config(noreplace) %{_sysconfdir}/pam.d/xdm
%config(noreplace) %{_sysconfdir}/logrotate.d/xdm
%dir /var/lib/xdm
%{_bindir}/xdm
%{_bindir}/xdmshell
%{_mandir}/man1/xdm.*
%{_mandir}/man1/xdmshell.*
%{xdm_libdir}/*
%{_datadir}/X11/app-defaults/Chooser
%{_unitdir}/xdm.service
