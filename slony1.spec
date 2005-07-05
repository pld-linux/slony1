#
# TODO:
#	- trigger for upgrading
#		e.g. stop slony1, warn user. No automatic upgrade possible (must be done all all nodes)
#
Summary:	Slony-I - a "master to multiple slaves" replication system for PostgreSQL
Summary(pl):	Slony-I - system replikacji dla PostgreSQL
Name:		slony1
Version:	1.1.0
Release:	0.1
Epoch:		0
License:	BSD
Group:		Applications/Databases
Source0:	http://developer.postgresql.org/~wieck/slony1/download/%{name}-%{version}.tar.bz2
Source1:	%{name}.init
Source2:	%{name}.pgpass
Source3:	%{name}.sysconfig
Patch0:		%{name}-no_server_for_build.patch
URL:		http://slony.info/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	postgresql-backend-devel
Conflicts: 	postgresql <= 8.0.3-3
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pgmoduledir	%{_libdir}/postgresql
%define		_pgsqldir	%{_datadir}/postgresql

%description
Slony-I is a "master to multiple slaves" replication system with
cascading and failover.

The big picture for the development of Slony-I is a master-slave
system that includes all features and capabilities needed to replicate
large databases to a reasonably limited number of slave systems.

Slony-I is a system for data centers and backup sites, where the
normal mode of operation is that all nodes are available. 

%description -l pl
Slony-I jest systemem replikacji dla PostgreSQL. Pozwala na replikacjê
typu "jeden serwer g³owny, wiele serwerów pomocniczych".

G³ówn± zalet± Slony-I jest system "master-slave". Zawiera on wszelk±
funkcjonalno¶æ potrzebn± do replikowania du¿ych baz danych na
okre¶lon± ilo¶æ serwerów pomocniczych lub zastêpczych.

Slony-I jest przeznaczony dla systemów, gdzie normalny tryb pracy
wymaga aby zarówno serwer g³ówny jak i wszystkie serwery pomocnicze
by³y ca³y czas operacyjne.

%prep
%setup -q
%patch0 -p1

%build
%{__aclocal} -I config
%{__autoconf}
cp /usr/share/automake/config.* config
%configure \
	--with-pgsharedir=%{_pgsqldir}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,/etc/sysconfig/slony1,/home/services/slony1}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/slony1
install %{SOURCE2} $RPM_BUILD_ROOT/home/services/slony1/.pgpass
install %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/slony1

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -P slony1 -g 131 -r slony1
%useradd -P slony1 -M -o -r -u 131 -d /home/services/slony1 -s /bin/sh -g slony1 -c "Slony-I Replicator" slony1

%post
/sbin/chkconfig --add slony1
if [ -f /var/lock/subsys/slony1 ]; then
	/etc/rc.d/init.d/slony1 restart >&2 || :
else
	echo "Run \"/etc/rc.d/init.d/slony1 start\" to start slony1 replicator."
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/slony1 ]; then
		/etc/rc.d/init.d/slony1 stop
	fi
	/sbin/chkconfig --del slony1
fi

%files
%defattr(644,root,root,755)
%doc HISTORY-1.1 README SAMPLE TODO UPGRADING doc/adminguide/prebuilt/* doc/*/*.txt
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_pgmoduledir}/*.so
%{_pgsqldir}/*
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(750,slony1,slony1) %dir /home/services/slony1
%attr(600,slony1,slony1) /home/services/slony1/.pgpass
