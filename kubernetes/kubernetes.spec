%global goipath k8s.io/kubernetes
%global forgeurl https://github.com/kubernetes/kubernetes
Version:        1.26.11
%global goname kubernetes

%gometa

%global commit0 3cd242c51317aed8858119529ccab22079f523b1

Name:           %{goname}
Release:        1%{?dist}
Summary:        Container cluster management
License:        ASL 2.0
URL:            %{gourl}
Source0:        %{gosource}
Source1:	10-kubeadm.conf
Source2:	kubelet
Source3:	kubelet.service

BuildRequires: systemd-rpm-macros

%description
%{summary}

%package -n kubelet
Summary: The node agent of Kubernetes, the container cluster manager.

Requires(pre): shadow-utils
Requires: socat
Requires: iptables-nft
Requires: conntrack-tools
Requires: containerd

%description -n kubelet
%{summary}

%package -n kubeadm
Summary:  Command-line utility for administering a Kubernetes cluster.

Requires: kubelet
Requires: cri-tools
Requires: kubectl
Requires: containernetworking-plugins

%description -n kubeadm
%{summary}

%package -n kubectl
Summary: Command-line utility for interacting with a Kubernetes cluster.

%description -n kubectl
%{summary}

%prep
%goprep -k

%build
export BUILDTAGS="selinux notest"
export buildDate=$(date --date=@${SOURCE_DATE_EPOCH} -u +'%Y-%m-%dT%H:%M:%SZ')
export gitCommit=%{commit0}
export gitTreeState=archive
export gitVersion=v%{version}
export gitMajor=$(echo %{version} | sed -r 's/^([0-9]+)\..*/\1/')
export gitMinor=$(echo %{version} | sed -r 's/^[0-9]+\.([0-9]+)\..*/\1/')
for key in buildDate gitCommit gitTreeState gitVersion gitMajor gitMinor; do
    export LDFLAGS+="-X %{goipath}/vendor/k8s.io/client-go/pkg/version.${key}=${!key} \
        -X %{goipath}/vendor/k8s.io/component-base/version.${key}=${!key} \
        -X k8s.io/client-go/pkg/version.${key}=${!key} \
        -X k8s.io/component-base/version.${key}=${!key} "
done

for cmd in cmd/{kubelet,kubeadm,kubectl}; do
    %gobuild -o %{gobuilddir}/bin/$(basename $cmd) %{goipath}/$cmd
done

%install
install -p -D -t %{buildroot}%{_bindir} %{gobuilddir}/bin/*

install -d -m 0755 %{buildroot}/%{_unitdir}/kubelet.service.d
install -p -m 0644 -t %{buildroot}/%{_unitdir}/kubelet.service.d %{SOURCE1}

install -d -m 0755 %{buildroot}%{_datadir}/bash-completion/completions/
%{buildroot}%{_bindir}/kubectl completion bash > %{buildroot}%{_datadir}/bash-completion/completions/kubectl

install -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}
install -d -m 0700 %{buildroot}%{_sysconfdir}/%{name}/manifests
install -D -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/kubelet

install -d -m 0755 %{buildroot}%{_unitdir}
install -m 0644 -t %{buildroot}%{_unitdir} %{SOURCE3}

%post -n kubelet
%systemd_post kubelet

%preun -n kubelet
%systemd_preun kubelet

%postun -n kubelet
%systemd_postun_with_restart kubelet

%files -n kubelet
%license LICENSE
%{_bindir}/kubelet
%{_unitdir}/kubelet.service
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/manifests
%config(noreplace) %{_sysconfdir}/sysconfig/kubelet

%files -n kubeadm
%license LICENSE
%{_bindir}/kubeadm
%dir %{_unitdir}/kubelet.service.d
%config(noreplace) %{_unitdir}/kubelet.service.d/10-kubeadm.conf

%files -n kubectl
%license LICENSE
%{_bindir}/kubectl
%{_datadir}/bash-completion/completions/kubectl

%changelog
* Fri Nov 17 2023 Karel Van Hecke <copr@karelvanhecke.com> - 1.26.11-1
- bump kubernetes to v1.26.11
* Sun Oct 22 2023 Karel Van Hecke <copr@karelvanhecke.com> - 1.26.10-1
- bump kubernetes to v1.26.10
* Fri Sep 15 2023 Karel Van Hecke <copr@karelvanhecke.com> - 1.26.9-1
- bump kubernetes to v1.26.9
* Sat Sep 02 2023 Karel Van Hecke <copr@karelvanhecke.com> - 1.26.8-1
- bump kubernetes to v1.26.8
* Wen Jul 26 2023 Karel Van Hecke <copr@karelvanhecke.com> - 1.26.7-1
- bump kubernetes to v1.26.7
* Mon Jun 05 2023 Karel Van Hecke <copr@karelvanhecke.com> - 1.26.4-4
- kubelet systemd service changes
* Sat May 27 2023 Karel Van Hecke <copr@karelvanhecke.com> - 1.26.4-3
- Update kubelet service and kubeadm dropin conf
* Thu May 25 2023 Karel Van Hecke <copr@karelvanhecke.com> - 1.26.4-2
- systemd unit update
* Sun May 14 2023 Karel Van Hecke <copr@karelvanhecke.com> - 1.26.4-1
- Bump to v1.26.4
* Tue Apr 18 2023 Karel Van Hecke <copr@karelvanhecke.com> - 1.25.9-1
- Bump to v1.25.9
* Sun Mar 26 2023 Karel Van Hecke <copr@karelvanhecke.com> - 1.25.8-1
- Initial build
