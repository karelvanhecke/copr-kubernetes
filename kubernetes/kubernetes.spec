%global _dwz_low_mem_die_limit 0

%global goipath github.com/kubernetes/kubernetes
Version:        1.26.0

%gometa

%global import_path             k8s.io/kubernetes

# Needed otherwise "version_ldflags=$(kube::version_ldflags)" doesn't work
%global _buildshell  /bin/bash

Name:           kubernetes
Release:        1%{?dist}
Summary:        Container cluster management
License:        ASL 2.0
URL:            %{gourl}
Source0:        %{gosource}
Source1:	10-kubeadm.conf
Source2:	kubelet
Source3:	kubelet.service

Patch0: build-with-debuginfo.patch

BuildRequires: make
BuildRequires: systemd
BuildRequires: rsync

%description
%{summary}

%package -n kubelet
Summary: The node agent of Kubernetes, the container cluster manager.

Requires(pre): shadow-utils
Requires: socat
Requires: iptables-nft
Requires: conntrack-tools
Requires: cri-o

%description -n kubelet
%{summary}

%package -n kubeadm
Summary:  Command-line utility for administering a Kubernetes cluster.

Requires: kubelet = %{version}-%{release}
Requires: cri-tools
Requires: kubectl = %{version}-%{release}
Requires: containernetworking-plugins

%description -n kubeadm
%{summary}

%package -n kubectl
Summary: Command-line utility for interacting with a Kubernetes cluster.

%description -n kubectl
%{summary}

%prep
%goprep -k
%autopatch -p1

%build
export GO111MODULE=off
export CGO_CPPFLAGS="-D_FORTIFY_SOURCE=2 -fstack-protector-all"

# Build each binary separately to generate a unique build-id.
make WHAT="cmd/kubelet"
make WHAT="cmd/kubeadm"
make WHAT="cmd/kubectl"

# Gen docs
hack/update-generated-docs.sh

%install
output_path="_output/bin"

install -m 755 -d %{buildroot}%{_bindir}
install -p -m 755 -t %{buildroot}%{_bindir} ${output_path}/kubelet
install -p -m 755 -t %{buildroot}%{_bindir} ${output_path}/kubeadm
install -p -m 755 -t %{buildroot}%{_bindir} ${output_path}/kubectl

install -d -m 0755 %{buildroot}/%{_unitdir}/kubelet.service.d
install -p -m 0644 -t %{buildroot}/%{_unitdir}/kubelet.service.d %{SOURCE1}

install -d -m 0755 %{buildroot}%{_datadir}/bash-completion/completions/
%{buildroot}%{_bindir}/kubectl completion bash > %{buildroot}%{_datadir}/bash-completion/completions/kubectl
install -d -m 0755 %{buildroot}%{_datadir}/zsh-completion/completions/
%{buildroot}%{_bindir}/kubectl completion zsh > %{buildroot}%{_datadir}/zsh-completion/completions/kubectl
install -d -m 0755 %{buildroot}%{_datadir}/fish-completion/completions/
%{buildroot}%{_bindir}/kubectl completion fish > %{buildroot}%{_datadir}/fish-completion/completions/kubectl

install -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}
install -d -m 0700 %{buildroot}%{_sysconfdir}/%{name}/manifests
install -D -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/kubelet

install -d -m 0755 %{buildroot}%{_unitdir}
install -m 0644 -t %{buildroot}%{_unitdir} %{SOURCE3}

install -d %{buildroot}%{_mandir}/man1
install -p -m 644 docs/man/man1/*.1 %{buildroot}%{_mandir}/man1
rm -f %{buildroot}%{_mandir}/man1/kube-{apiserver,controller-manager,proxy,scheduler}.1*

%post -n kubelet
%systemd_post kubelet

%preun -n kubelet
%systemd_preun kubelet

%postun -n kubelet
%systemd_postun kubelet

%files -n kubelet
%license LICENSE
%doc *.md
%{_mandir}/man1/kubelet.1*
%{_bindir}/kubelet
%{_unitdir}/kubelet.service
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/manifests
%config(noreplace) %{_sysconfdir}/sysconfig/kubelet

%files -n kubeadm
%license LICENSE
%doc *.md
%{_mandir}/man1/kubeadm.1*
%{_mandir}/man1/kubeadm-*
%{_bindir}/kubeadm
%dir %{_unitdir}/kubelet.service.d
%config(noreplace) %{_unitdir}/kubelet.service.d/10-kubeadm.conf

%files -n kubectl
%license LICENSE
%doc *.md
%{_mandir}/man1/kubectl.1*
%{_mandir}/man1/kubectl-*
%{_bindir}/kubectl
%{_datadir}/bash-completion/completions/kubectl
%{_datadir}/zsh-completion/completions/kubectl
%{_datadir}/fish-completion/completions/kubectl

%changelog
* Sun Dec 11 2022 Karel Van Hecke <copr@karelvanhecke.com> - 1.26.0-1
- Bump to v1.26.0
* Sat Dec 10 2022 Karel Van Hecke <copr@karelvanhecke.com> - 1.25.5-1
- Initial build
