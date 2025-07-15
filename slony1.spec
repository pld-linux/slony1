# TODO:
# - trigger for upgrading
#   e.g. stop slony1, warn user. No automatic upgrade possible (must be done all all nodes)
# - move slony-tools.pm to some better place
# - there is 1.2 line - upgrade it
#
Summary:	Slony-I - a "master to multiple slaves" replication system for PostgreSQL
Summary(pl.UTF-8):	Slony-I - system replikacji dla PostgreSQL
Name:		slony1
Version:	1.1.9
Release:	1
Epoch:		0
License:	BSD
Group:		Applications/Databases
Source0:	http://main.slony.info/downloads/1.1/source/%{name}-%{version}.tar.bz2
# Source0-md5:	267a733408aeaae48ce514e309fc4dab
Source1:	%{name}.init
Source2:	%{name}.pgpass
Source3:	%{name}.sysconfig
Patch0:		%{name}-no_server_for_build.patch
Patch1:		%{name}-pgsql82.patch
URL:		http://slony.info/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	postgresql-backend-devel >= 8.2.0
# for libpgport.a (move to postgresql-backend-devel?)
BuildRequires:	postgresql-static >= 8.2.0
BuildRequires:	rpm-perlprov
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts
Conflicts:	postgresql <= 8.0.3-3
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pgmoduledir	%{_libdir}/postgresql
%define		_pgsqldir	%{_datadir}/postgresql

%define         _noautoreq      '%{_libdir}//slon-tools.pm'

%description
Slony-I is a "master to multiple slaves" replication system with
cascading and failover.

The big picture for the development of Slony-I is a master-slave
system that includes all features and capabilities needed to replicate
large databases to a reasonably limited number of slave systems.

Slony-I is a system for data centers and backup sites, where the
normal mode of operation is that all nodes are available.

%description -l pl.UTF-8
Slony-I jest systemem replikacji dla PostgreSQL. Pozwala na replikację
typu "jeden serwer głowny, wiele serwerów pomocniczych".

Główną zaletą Slony-I jest system "master-slave". Zawiera on wszelką
funkcjonalność potrzebną do replikowania dużych baz danych na
określoną ilość serwerów pomocniczych lub zastępczych.

Slony-I jest przeznaczony dla systemów, gdzie normalny tryb pracy
wymaga aby zarówno serwer główny jak i wszystkie serwery pomocnicze
były cały czas operacyjne.

%package altperl
Summary:	Perl scripts for managing Slony-I
Summary(pl.UTF-8):	Skrypty perlowe do zarządzania Slony-I
Group:		Applications/Databases
Requires:	%{name} = %{epoch}:%{version}-%{release}
Requires:	perl-modules

%description altperl
The altperl scripts provide an alternate method of managing Slony-I,
generating slonik scripts and monitoring slon daemons. They support an
arbitrary number of Slony-I nodes in clusters of various shapes and
sizes.

%description altperl -l pl.UTF-8
Skrypty altperl dostarczają alternatywną metodę zarządzania Slony-I,
generując skrypty slonik i monitorując demony slon. Obsługują dowolną
liczbę węzłów Slony-I w klastrach różnych kształtów i rozmiarów.

%package tools
Summary:	Useful additional scripts for Slony-I
Summary(pl.UTF-8):	Przydatne dodatkowe skrypty dla Slony-I
Group:		Applications/Databases
Requires:	%{name} = %{epoch}:%{version}-%{release}
Requires:	perl-modules

%description tools
This package contains some additional scripts provided with Slony-I,
useful for Slony-I setup, maintainance or monitoring.

%description tools -l pl.UTF-8
Ten pakiet dostarcza różne dodatkowe skrypty zawarte w źródłach
Slony-I, przydatne do konfiguracji, zarządzania i monitorowania tym
systemem.

%prep
%setup -q
%patch -P0 -p1
%patch -P1 -p1

sed -i -e 's,^#!/usr/bin/env perl,^#!/usr/bin/perl,' tools/*.pl

%build
%{__aclocal} -I config
%{__autoconf}
cp /usr/share/automake/config.* config
%configure \
	--with-pgsharedir=%{_pgsqldir} \
	--with-perltools
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,/etc/sysconfig,/home/services/slony1}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/slony1
install %{SOURCE2} $RPM_BUILD_ROOT/home/services/slony1/.pgpass
install %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/slony1
mv $RPM_BUILD_ROOT%{_sysconfdir}/slon_tools.conf{-sample,}
install tools/{check_*.sh,generate_syncs.sh,slony1_*.sh,slony_setup.pl} $RPM_BUILD_ROOT%{_bindir}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -P slony1 -g 131 -r slony1
%useradd -P slony1 -M -o -r -u 131 -d /home/services/slony1 -s /bin/sh -g slony1 -c "Slony-I Replicator" slony1

%post
/sbin/chkconfig --add slony1
%service slony1 restart "slony1 replicator"

%preun
if [ "$1" = "0" ]; then
	%service slony1 stop
	/sbin/chkconfig --del slony1
fi

%files
%defattr(644,root,root,755)
%doc HISTORY-1.1 README SAMPLE TODO UPGRADING doc/*/*.txt
%attr(755,root,root) %{_bindir}/slon
%attr(755,root,root) %{_bindir}/slonik
%attr(755,root,root) %{_pgmoduledir}/*.so
%{_pgsqldir}/*
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(750,slony1,slony1) %dir /home/services/slony1
%attr(600,slony1,slony1) /home/services/slony1/.pgpass

%files altperl
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/slonik_*
%attr(755,root,root) %{_bindir}/slon_*
%attr(755,root,root) %{_bindir}/slony_*
%attr(755,root,root) %{_bindir}/show_configuration
%{_libdir}/*.pm
%{_sysconfdir}/slon_tools.conf

%files tools
%defattr(644,root,root,755)
%doc tools/README*
%attr(755,root,root) %{_bindir}/*.sh
%attr(755,root,root) %{_bindir}/*.pl
