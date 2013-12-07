%define with_consolekit 1
%define xdm_libdir %{_datadir}/X11/xdm

Name:		xdm
Version:	1.1.11
Release:	5
Summary:	X Display Manager with support for XDMCP
Group:		System/X11
License:	MIT
URL:		http://xorg.freedesktop.org
Source0:	http://xorg.freedesktop.org/releases/individual/app/%{name}-%{version}.tar.bz2
Source1:	xdm.pamd
Patch4:		0004-Support-kdm-extended-syntax-to-reserve-a-server-for.patch
#Patch5: 0005-Initialize-the-greeter-only-after-checking-if-the-th.patch
Patch6:		0006-Add-console-kit-support-to-xdm.patch
Patch7:		0007-Add-files-required-by-consolekit-support.patch
Patch8:		xdm-1.1.11-fix-service-file.patch

BuildRequires:	pkgconfig(x11) >= 1.0.0
BuildRequires:	pkgconfig(xau) >= 1.0.0
BuildRequires:	pkgconfig(xaw7) >= 1.0.1
BuildRequires:	pkgconfig(xdmcp) >= 1.0.0
BuildRequires:	pkgconfig(xmu) >= 1.0.0
BuildRequires:	pkgconfig(xorg-macros) >= 1.3.0
BuildRequires:	pkgconfig(xt) >= 1.0.0
BuildRequires:	pam-devel
%if %{with_consolekit}
%if %mdvver < 201300
BuildRequires:	pkgconfig(ck-connector)
%endif
BuildRequires:	pkgconfig(dbus-1)
%endif
Requires:	xinitrc > 2.4.19-9
Requires:	xrdb
Requires:	sessreg
Conflicts:	xorg-x11 < 7.0

%description
Xdm manages a collection of X displays, which may be on the local host or
remote servers. The design of xdm was guided by the needs of X terminals as
well as The Open Group standard XDMCP, the X Display Manager Control Protocol.
Xdm provides services similar to those provided by init, getty and login on
character terminals: prompting for login name and password, authenticating the
user, and running a session.

%prep
%setup -q
%apply_patches

%build
# patch 6 requires autoreconf
autoreconf -v --install
%configure2_5x \
	--x-includes=%{_includedir}\
	--x-libraries=%{_libdir} \
%if %{with_consolekit}
%if %mdvver < 201300
	--with-consolekit \
%else
	--without-consolekit \
%endif
%endif
	--with-xdmlibdir=%{xdm_libdir} \
	--with-pam \
%if %mdvver >= 201300
	--with-systemdsystemunitdir=%{_unitdir} \
%endif
	--enable-xdmshell


%make

%install
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
%if %mdvver >= 201300
%{_unitdir}/xdm.service
%endif

%changelog
* Sat Dec 31 2011 Matthew Dawkins <mattydaw@mandriva.org> 1.1.11-1
+ Revision: 748532
- fixed files list
- add enable-xdmshell
- removed fuzz from p 0006
- rediffed patches 0004 and 0006
- fixed BR
- new version 1.1.11
- cleaned up spec
- converted BRs to pkgconfig provides

* Sat May 07 2011 Oden Eriksson <oeriksson@mandriva.com> 1.1.10-3
+ Revision: 671297
- mass rebuild

* Sat Dec 04 2010 Oden Eriksson <oeriksson@mandriva.com> 1.1.10-2mdv2011.0
+ Revision: 608199
- rebuild

* Mon Apr 12 2010 Paulo Ricardo Zanoni <pzanoni@mandriva.com> 1.1.10-1mdv2010.1
+ Revision: 533690
- New version: 1.1.10
- Rename console-kit patch

* Mon Apr 05 2010 Paulo Ricardo Zanoni <pzanoni@mandriva.com> 1.1.9-1mdv2010.1
+ Revision: 531812
- New version: 1.1.9
- Call autoreconf (needed by consolekit patch) and BR x11-util-macros
- Temporarily disable patch 5 since it's undocumented and looks suspicious

* Wed Mar 17 2010 Oden Eriksson <oeriksson@mandriva.com> 1.1.8-5mdv2010.1
+ Revision: 524423
- rebuilt for 2010.1

* Fri Oct 02 2009 Thierry Vignaud <tv@mandriva.org> 1.1.8-4mdv2010.0
+ Revision: 452589
- source 1: use pam_namespace for xguest

* Sat Mar 07 2009 Antoine Ginies <aginies@mandriva.com> 1.1.8-3mdv2009.1
+ Revision: 351203
- rebuild

* Thu Aug 07 2008 Thierry Vignaud <tv@mandriva.org> 1.1.8-2mdv2009.0
+ Revision: 266078
- rebuild early 2009.0 package (before pixel changes)

* Fri May 23 2008 Paulo Andrade <pcpa@mandriva.com.br> 1.1.8-1mdv2009.0
+ Revision: 210730
- o Update to version 1.1.8
  o Don't create a symlink from /usr/lib/X11 to /etc/X11, neither be the
  owner of that symlink.
  o Modify requires of xinitrc to versioned.

* Mon Apr 14 2008 Thierry Vignaud <tv@mandriva.org> 1.1.7-1mdv2009.0
+ Revision: 193164
- adjust file list
- new release

* Tue Feb 12 2008 Paulo Andrade <pcpa@mandriva.com.br> 1.1.6-6mdv2008.1
+ Revision: 166484
- Revert to use upstream tarball, build requires and remove non mandatory local patches.

* Mon Jan 21 2008 Paulo Andrade <pcpa@mandriva.com.br> 1.1.6-5mdv2008.1
+ Revision: 155923
- Add xdm patches to git repository, update build requires and resubmit.
- Check range and correct format string.

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Thu Sep 13 2007 Paulo Andrade <pcpa@mandriva.com.br> 1.1.6-4mdv2008.0
+ Revision: 85182
- Increase release and add change commented in previous commit, but that ended
  not being added when merging the 2 ConsoleKit related patches.
- Merge changes to only one patch (fix a close instead of close) and should also
  implement the only feature left missing from the Kdm patch, that is the remote
  server name in case of non local connection.
  If there are no bugs associated with proper setting the XDG_SESSION_COOKIE
  environment variable, it should be as functional to ConsoleKit as Kdm.
- Err, it really isn't either %%d or %%x, but %%d should work correctly for the first
  99 virtual terminals.

* Thu Sep 13 2007 Paulo Andrade <pcpa@mandriva.com.br> 1.1.6-3mdv2008.0
+ Revision: 85138
- Add a X Server 'tty' detection code to provide the proper 'x11-display-device'
  field to dbus.

* Wed Sep 12 2007 Paulo Andrade <pcpa@mandriva.com.br> 1.1.6-2mdv2008.0
+ Revision: 84808
- First release with KDM's ConsoleKit path adpated to XDM.

* Fri Aug 17 2007 Thierry Vignaud <tv@mandriva.org> 1.1.6-1mdv2008.0
+ Revision: 64747
- new release

* Fri Aug 10 2007 Thierry Vignaud <tv@mandriva.org> 1.1.5-1mdv2008.0
+ Revision: 61657
- fix man extension
- new release


* Thu Feb 15 2007 Thierry Vignaud <tvignaud@mandriva.com> 1.1.4-1mdv2007.0
+ Revision: 121448
- new release

* Tue Feb 06 2007 Gustavo Pichorim Boiko <boiko@mandriva.com> 1.1.3-1mdv2007.1
+ Revision: 116787
- new upstream version: 1.1.3

* Thu Dec 14 2006 Thierry Vignaud <tvignaud@mandriva.com> 1.1.2-1mdv2007.1
+ Revision: 97066
- new release

* Tue Nov 21 2006 Thierry Vignaud <tvignaud@mandriva.com> 1.1.1-1mdv2007.1
+ Revision: 85959
- new release

* Tue Aug 29 2006 Gustavo Pichorim Boiko <boiko@mandriva.com> 1.0.5-5mdv2007.0
+ Revision: 58564
- fix the upgrade in cases where /usr/lib/X11/xdm/authdir is a
  directory (#24774)

* Tue Aug 15 2006 Pixel <pixel@mandriva.com> 1.0.5-4mdv2007.0
+ Revision: 56059
- fix group
- make /etc/X11/xdm/xdm-config accessible
- add requires sessreg (used by GiveConsole and TakeConsole)
- restore authdir symlink to /var/lib/xdm (otherwise xdm writes temp stuff in /usr)

  + Gustavo Pichorim Boiko <boiko@mandriva.com>
    - pam_stack is deprecated. Fixed the xdm.pamd file
    - enable missing pam support

* Sat Jun 24 2006 Gustavo Pichorim Boiko <boiko@mandriva.com> 1.0.5-1mdv2007.0
+ Revision: 37943
- new upstream release (1.0.5):
  * setuid return value check fix
- adding xdm.pamd to the sources list
- add pam and logrotate files (Closes #22589)
- added patch: Support kdm extended syntax to reserve a server for future use
  but do nothing
- added patch: Initialize the greeter only after checking if the the required
  steps are ok
- rebuild to fix cooker uploading
- X11R7.1
- increment release
- Adding X.org 7.0 to the repository

  + Andreas Hasenack <andreas@mandriva.com>
    - renamed mdv to packages because mdv is too generic and it's hosting only packages anyway

  + Thierry Vignaud <tvignaud@mandriva.com>
    - fill in more missing descriptions

  + Pixel <pixel@mandriva.com>
    - we need libXdmGreet.so

