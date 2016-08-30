# (c) 2014 Amplify Education, Inc. All rights reserved, subject to the license
# below.
#
# Education agencies that are members of the Smarter Balanced Assessment
# Consortium as of August 1, 2014 are granted a worldwide, non-exclusive, fully
# paid-up, royalty-free, perpetual license, to access, use, execute, reproduce,
# display, distribute, perform and create derivative works of the software
# included in the Reporting Platform, including the source code to such software.
# This license includes the right to grant sublicenses by such consortium members
# to third party vendors solely for the purpose of performing services on behalf
# of such consortium member educational agencies.

Name:		edsftp%(echo ${SFTP_ENV_NAME:=""})
Version:	%(echo ${RPM_VERSION:="X.X"})
Release:	%(echo ${BUILD_NUMBER:="X"})%{?dist}
Summary:	Edware's SFTP Box
Group:		SFTP
License: Amplify Education, Inc and ASL 2.0
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
Vendor: Amplify Insight Edware Team <edwaredev@wgen.net>
Url: https://github.wgenhq.net/Ed-Ware-SBAC/edware

BuildRequires:	python3
BuildRequires:	python3-libs
Requires:	python3-libs
AutoReqProv: no

%define _unpackaged_files_terminate_build 0
# disable the default cleanup of build root
%define __spec_install_pre %{___build_pre}

%description
EdWare SFTP
commit: %(echo ${GIT_COMMIT:="UNKNOWN"})


%prep
rm -rf virtualenv/edsftp
rm -rf %{buildroot}
mkdir -p %{buildroot}/opt/edware
cp -r ${WORKSPACE}/edsftp %{buildroot}/opt/edware
mkdir -p %{buildroot}/opt/edware/conf
mkdir -p %{buildroot}/etc/rc.d/init.d
cp ${WORKSPACE}/edsftp/config/linux/etc/rc.d/init.d/edsftp-watcher %{buildroot}/etc/rc.d/init.d/
cp ${WORKSPACE}/config/generate_ini.py %{buildroot}/opt/edware/conf/
cp ${WORKSPACE}/config/settings.yaml %{buildroot}/opt/edware/conf/

%build
export LANG=en_US.UTF-8
virtualenv-3.3 --distribute virtualenv/edsftp
source virtualenv/edsftp/bin/activate

cd ${WORKSPACE}/config
python setup.py clean --all
python setup.py install
cd -
cd ${WORKSPACE}/edcore
python setup.py clean --all
python setup.py install
cd -
cd ${WORKSPACE}/edauth
python setup.py clean --all
python setup.py install
cd -
cd ${WORKSPACE}/edapi
python setup.py clean --all
python setup.py install
cd -
cd ${WORKSPACE}/edsftp
python setup.py clean --all
python setup.py install
cd -
cd ${WORKSPACE}/smarter_common
python setup.py clean --all
python setup.py install
cd -

deactivate

%install
mkdir -p %{buildroot}/opt/virtualenv
cp -r virtualenv/edsftp %{buildroot}/opt/virtualenv
find %{buildroot}/opt/virtualenv/edsftp/bin -type f -exec sed -i -r 's/(\/[^\/]*)*\/rpmbuild\/BUILD/\/opt/g' {} \;

%clean
rm -rf %{buildroot}

%files
%defattr(644,root,root,755)
/opt/edware/conf/generate_ini.py
/opt/edware/conf/settings.yaml
/opt/virtualenv/edsftp/include/*
/opt/virtualenv/edsftp/lib/*
/opt/virtualenv/edsftp/lib64
/opt/virtualenv/edsftp/bin/activate
/opt/virtualenv/edsftp/bin/activate.csh
/opt/virtualenv/edsftp/bin/activate.fish
/opt/virtualenv/edsftp/bin/activate_this.py
%attr(755,root,root) /opt/virtualenv/edsftp/bin/easy_install
%attr(755,root,root) /opt/virtualenv/edsftp/bin/easy_install-3.3
%attr(755,root,root) /opt/virtualenv/edsftp/bin/sftp_driver.py
%attr(755,root,root) /opt/virtualenv/edsftp/bin/pip
%attr(755,root,root) /opt/virtualenv/edsftp/bin/pip3
%attr(755,root,root) /opt/virtualenv/edsftp/bin/python3.3
%attr(755,root,root) /opt/virtualenv/edsftp/bin/python
%attr(755,root,root) /opt/virtualenv/edsftp/bin/python3
%attr(755,root,root) /etc/rc.d/init.d/edsftp-watcher

%pre
EDWARE_ROOT=/opt/edware
if [ ! -d $EDWARE_ROOT/ssh ]; then
    mkdir -p $EDWARE_ROOT/ssh
fi

if [ ! -d $EDWARE_ROOT/ssh/.ssh ]; then
    mkdir -p $EDWARE_ROOT/ssh/.ssh
fi

if [ ! -d /var/run/edsftp-watcher ]; then
    mkdir -p /var/run/edsftp-watcher
fi

if [ ! -d /var/log/edsftp-watcher ]; then
    mkdir -p /var/log/edsftp-watcher
fi

%post
chkconfig --add edsftp-watcher
chkconfig --level 2345 edsftp-watcher off

%preun
chkconfig --del edsftp-watcher

%postun

%changelog
