%define unmangled_name protonvpn-gui
%define version 0.0.3
%define release 1

Prefix: %{_prefix}

Name: %{unmangled_name}
Version: %{version}
Release: %{release}
Summary: Official ProtonVPN GUI

Group: ProtonVPN
License: GPLv3
Url: https://github.com/ProtonVPN
Vendor: Proton Technologies AG <opensource@proton.me>
Source0: %{unmangled_name}-%{version}.tar.gz
Group: Development/Libraries
BuildArch: noarch
BuildRoot: %{_tmppath}/%{unmangled_name}-%{version}-%{release}-buildroot

BuildRequires: python3-devel
BuildRequires: python3-setuptools
Requires: python3-protonvpn-nm-lib >= 0.5.0, python3-protonvpn-nm-lib < 0.6.0
Requires: python3-gobject
Requires: gtk3

%{?python_disable_dependency_generator}

%description
Official ProtonVPN Graphical User Interface.


%prep
%setup -n %{unmangled_name}-%{version} -n %{unmangled_name}-%{version}

%build
python3 setup.py build

%install
python3 setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%{python3_sitelib}/linux_app/
%{python3_sitelib}/linux_app-%{version}*.egg-info/
%defattr(-,root,root)

%changelog
* Mon Feb 22 2021 Proton Technologies AG <opensource@proton.me> 0.0.3-1
- First package

