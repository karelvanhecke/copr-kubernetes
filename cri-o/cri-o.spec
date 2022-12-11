# https://github.com/cri-o/cri-o
%global goipath         github.com/cri-o/cri-o
Version:                1.26.0

%if 0%{?rhel} && 0%{?rhel} <= 8
%define gobuild(o:) %{expand:
  # https://bugzilla.redhat.com/show_bug.cgi?id=995136#c12
  %global _dwz_low_mem_die_limit 0
  %ifnarch ppc64
  go build -buildmode pie -compiler gc -tags="rpm_crashtraceback ${BUILDTAGS:-}" -ldflags "${BASE_LDFLAGS:-}%{?currentgoldflags} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n') -extldflags '%__global_ldflags %{?__golang_extldflags}' -compressdwarf=false" -a -v -x %{?**};
  %else
  go build                -compiler gc -tags="rpm_crashtraceback ${BUILDTAGS:-}" -ldflags "${BASE_LDFLAGS:-}%{?currentgoldflags} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n') -extldflags '%__global_ldflags %{?__golang_extldflags}' -compressdwarf=false" -a -v -x %{?**};
  %endif
}
%bcond_with check
%else
%gometa
%bcond_without check
%endif

# Related: github.com/cri-o/cri-o/issues/3684
%global build_timestamp %(date -u +'%Y-%m-%dT%H:%M:%SZ')
%global git_tree_state clean
%global criocli_path ""

# Used for comparing with latest upstream tag
# to decide whether to autobuild (non-rawhide only)
%global built_tag v%{version}
%global built_tag_strip %(b=%{built_tag}; echo ${b:1})
%global crio_release_tag %(echo %{built_tag_strip} | cut -f1,2 -d'.')

# Services
%global service_name crio

# Commit for the builds
%global commit0 c187a0c0a8f0f2162326dc07a1b770a1d7c6398f

Name:           cri-o
Epoch:          0
Release:        1.c187a0c%{?dist}
Summary:        Open Container Initiative-based implementation of Kubernetes Container Runtime Interface


# Upstream license specification: Apache-2.0
License:        ASL 2.0
URL:            https://github.com/cri-o/cri-o
Source0:        https://github.com/cri-o/cri-o/archive/refs/heads/release-1.26.zip

%if 0%{?rhel}
BuildRequires:  golang >= 1.18
%endif
%if 0%{?rhel} && 0%{?rhel} <= 8
# e.g. el6 has ppc64 arch without gcc-go, so EA tag is required
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 aarch64 %{arm}}
%else
# required for el9 and all fedora
BuildRequires:  go-rpm-macros
%endif
%if 0%{?fedora}
BuildRequires:  btrfs-progs-devel
BuildRequires:  device-mapper-devel
%endif
BuildRequires:  git-core
BuildRequires:  glib2-devel
BuildRequires:  glibc-static
BuildRequires:  go-md2man
BuildRequires:  gpgme-devel
BuildRequires:  libassuan-devel
BuildRequires:  libseccomp-devel
%if 0%{?rhel} && 0%{?rhel} < 8
BuildRequires:  systemd-devel
%else
BuildRequires:  systemd-rpm-macros
%endif
BuildRequires:  make
%if 0%{?fedora}
Requires(pre):  container-selinux
%else
Requires:       container-selinux
%endif
Requires:       containers-common >= 1:0.1.31-14
%if 0%{?rhel} && 0%{?rhel} < 8
Requires:       runc >= 1.0.0-16
Requires:       containernetworking-plugins >= 1.0.0-1
%else
Recommends:     runc >= 1.0.0-16
Suggests:       containernetworking-plugins >= 1.0.0-1
%endif
Requires:       conmon >= 2.0.2-1
Requires:       socat

Obsoletes:      ocid <= 0.3
Provides:       ocid = %{epoch}:%{version}-%{release}
Provides:       %{service_name} = %{epoch}:%{version}-%{release}

%description
Open Container Initiative-based implementation of Kubernetes Container Runtime
Interface.

%prep
%if 0%{?rhel} && 0%{?rhel} <= 8
%autosetup -p1 -n %{name}-release-1.26
%else
%goprep -k
%endif

sed -i 's/install.config: crio.conf/install.config:/' Makefile
sed -i 's/install.bin: binaries/install.bin:/' Makefile
sed -i 's/install.man: $(MANPAGES)/install.man:/' Makefile
sed -i 's/\.gopathok //' Makefile
sed -i 's/module_/module-/' internal/version/version.go
sed -i 's/\/local//' contrib/systemd/%{service_name}.service
sed -i 's/\/local//' contrib/systemd/%{service_name}-wipe.service

%build
export GO111MODULE=on
export GOFLAGS=-mod=vendor

export BUILDTAGS="$(hack/btrfs_installed_tag.sh)
$(hack/btrfs_tag.sh) $(hack/libdm_installed.sh)
$(hack/libdm_no_deferred_remove_tag.sh)
$(hack/seccomp_tag.sh)
$(hack/selinux_tag.sh)"

%if 0%{?centos} && 0%{?centos} <= 8
BUILDTAGS="$BUILDTAGS containers_image_openpgp"
%endif

export BASE_LDFLAGS="-X %{goipath}/internal/pkg/criocli.DefaultsPath=%{criocli_path}
-X  %{goipath}/internal/version.buildDate=%{build_timestamp}
-X  %{goipath}/internal/version.gitCommit=%{commit0}
-X  %{goipath}/internal/version.version=%{version}
-X  %{goipath}/internal/version.gitTreeState=%{git_tree_state} "

for cmd in cmd/* ; do
  %gobuild -o bin/$(basename $cmd) %{goipath}/$cmd
done

%if 0%{?fedora}
%set_build_flags
%endif
export CFLAGS="$CFLAGS -std=c99"
%make_build bin/pinns
GO_MD2MAN=go-md2man make docs

%install
sed -i 's/\/local//' contrib/systemd/%{service_name}.service
bin/%{service_name} \
      --selinux \
      --cni-plugin-dir /opt/cni/bin \
      --cni-plugin-dir "%{_libexecdir}/cni" \
      --enable-metrics \
      --metrics-port 9537 \
      config > %{service_name}.conf

# install binaries
install -dp %{buildroot}{%{_bindir},%{_libexecdir}/%{service_name}}
install -p -m 755 bin/%{service_name} %{buildroot}%{_bindir}

# install conf files
install -dp %{buildroot}%{_sysconfdir}/cni/net.d
install -p -m 644 contrib/cni/10-crio-bridge.conf %{buildroot}%{_sysconfdir}/cni/net.d/100-crio-bridge.conf
install -p -m 644 contrib/cni/99-loopback.conf %{buildroot}%{_sysconfdir}/cni/net.d/200-loopback.conf

install -dp %{buildroot}%{_sysconfdir}/%{service_name}
install -dp %{buildroot}%{_datadir}/containers/oci/hooks.d
install -dp %{buildroot}%{_datadir}/oci-umount/oci-umount.d
install -p -m 644 crio.conf %{buildroot}%{_sysconfdir}/%{service_name}
#install -p -m 644 seccomp.json %%{buildroot}%%{_sysconfdir}/%%{service_name}
install -p -m 644 crio-umount.conf %{buildroot}%{_datadir}/oci-umount/oci-umount.d/%{service_name}-umount.conf
install -p -m 644 crictl.yaml %{buildroot}%{_sysconfdir}

%make_install PREFIX=%{buildroot}%{_prefix} \
            install.bin \
            install.completions \
            install.config \
            install.man \
            install.systemd

%if 0%{?rhel} && 0%{?rhel} <= 7
# https://bugzilla.redhat.com/show_bug.cgi?id=1823374#c17
install -d -p %{buildroot}%{_prefix}/lib/sysctl.d
echo "fs.may_detach_mounts=1" > %{buildroot}%{_prefix}/lib/sysctl.d/99-cri-o.conf
%endif

install -dp %{buildroot}%{_sharedstatedir}/containers

%post
# Old verions of kernel do not recognize metacopy option.
# Reference: github.com/cri-o/cri-o/issues/3631
%if 0%{?rhel} && 0%{?rhel} <= 7
sed -i -e 's/,metacopy=on//g' /etc/containers/storage.conf
%sysctl_apply 99-cri-o.conf
%endif
%systemd_post %{service_name}

%preun
%systemd_preun %{service_name}

%postun
%systemd_postun_with_restart %{service_name}

%files
%license LICENSE
%doc docs code-of-conduct.md tutorial.md ADOPTERS.md CONTRIBUTING.md README.md
%doc awesome.md transfer.md
%{_bindir}/%{service_name}
%{_bindir}/%{service_name}-status
%{_bindir}/pinns
%{_mandir}/man5/%{service_name}.conf*5*
%{_mandir}/man8/%{service_name}*.8*
%dir %{_sysconfdir}/%{service_name}
%config(noreplace) %{_sysconfdir}/%{service_name}/%{service_name}.conf
%config(noreplace) %{_sysconfdir}/cni/net.d/100-%{service_name}-bridge.conf
%config(noreplace) %{_sysconfdir}/cni/net.d/200-loopback.conf
%config(noreplace) %{_sysconfdir}/crictl.yaml
%dir %{_libexecdir}/%{service_name}
%{_unitdir}/%{service_name}.service
%{_unitdir}/%{service_name}-wipe.service
%dir %{_sharedstatedir}/containers
%dir %{_datadir}/containers
%dir %{_datadir}/containers/oci
%dir %{_datadir}/containers/oci/hooks.d
%dir %{_datadir}/oci-umount
%dir %{_datadir}/oci-umount/oci-umount.d
%{_datadir}/oci-umount/oci-umount.d/%{service_name}-umount.conf
%{_datadir}/bash-completion/completions/%{service_name}*
%{_datadir}/fish/completions/%{service_name}*.fish
%{_datadir}/zsh/site-functions/_%{service_name}*
%if 0%{?rhel} && 0%{?rhel} <= 7
%{_prefix}/lib/sysctl.d/99-cri-o.conf
%endif

%changelog
* Sun Dec 11 2022 Karel Van Hecke <copr@karelvanhecke.com> - 0:1.26.0-1.c187a0c
- Bump to release-1.26, commit c187a0c
* Sat Dec 10 2022 Karel Van Hecke <copr@karelvanhecke.com> - 0:1.25.1-1
- Initial build
