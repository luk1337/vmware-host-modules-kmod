# buildforkernels macro hint: when you build a new version or a new release
# that contains bugfixes or other improvements then you must disable the
# "buildforkernels newest" macro for just that build; immediately after
# queuing that build enable the macro again for subsequent builds; that way
# a new akmod package will only get build when a new one is actually needed
%if 0%{?fedora}
%global buildforkernels akmod
%global debug_package %{nil}
%endif

Name:       vmware-host-modules-kmod
Summary:    Kernel module (kmod) for vmware-host-modules
Version:    16.1.0
Release:    1%{?dist}
License:    GPLv2
URL:        https://github.com/mkubecek/vmware-host-modules
Source0:    https://github.com/mkubecek/vmware-host-modules/archive/refs/heads/player-%{version}.tar.gz


BuildRequires:    %{_bindir}/kmodtool
%{!?kernels:BuildRequires: gcc, elfutils-libelf-devel, buildsys-build-rpmfusion-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu} }

# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
This package provides the vmware host kernel modules. You must also install
the vmware-player in order to make use of these modules.

%prep
# error out if there was something wrong with kmodtool
%{?kmodtool_check}

# print kmodtool output for debugging purposes:
kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%autosetup -c -T -a 0 -p 0
for kernel_version in %{?kernel_versions} ; do
    cp -a vmware-host-modules-player-%{version} _kmod_build_${kernel_version%%___*}
done

%build
for kernel_version in %{?kernel_versions}; do
    pushd _kmod_build_${kernel_version%%___*}
        %make_build -C ${kernel_version##*___} \
            M=${PWD}/vmmon-only \
            SRCROOT=${PWD}/vmmon-only \
            VM_KBUILD=1
        %make_build -C ${kernel_version##*___} \
            M=${PWD}/vmnet-only \
            SRCROOT=${PWD}/vmnet-only \
            VM_KBUILD=1
    popd
done

%install
for kernel_version  in %{?kernel_versions} ; do
    install -D -m 0755 _kmod_build_${kernel_version%%___*}/vmmon-only/vmmon.ko %{buildroot}/%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}vmmon.ko
    install -D -m 0755 _kmod_build_${kernel_version%%___*}/vmnet-only/vmnet.ko %{buildroot}/%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}vmnet.ko
done
%{?akmod_install}

%changelog
* Tue Mar 23 2021 Łukasz Patron <priv.luk@gmail.com> - player-16.1.0-1
- Release player-16.1.0
