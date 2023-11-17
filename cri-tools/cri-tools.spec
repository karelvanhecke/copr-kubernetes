%global goipath github.com/kubernetes-sigs/cri-tools
Version: 1.27.1
%global goname cri-tools

%gometa

Name: %{goname}
Release: 1%{?dist}
Summary: CLI and validation tools for Container Runtime Interface
License: ASL 2.0
URL: %{gourl}
Source0: %{gosource}

%description
%{summary}

%prep
%goprep -k

%build
export LDFLAGS="-X %{goipath}/pkg/version.Version=v%{version} "
%gobuild -o %{gobuilddir}/bin/crictl %{goipath}/cmd/crictl

%install
install -m 0755 -vd                     %{buildroot}%{_bindir}
install -m 0755 -vp %{gobuilddir}/bin/* %{buildroot}%{_bindir}/

%files
%license LICENSE
%{_bindir}/*

%changelog
* Fri Nov 17 2023 Karel Van Hecke <copr@karelvanhecke.com> - 1.27.1-1
- bump cri-tools to v1.27.1
* Sun May 14 2023 Karel Van Hecke <copr@karelvanhecke.com> - 1.26.1-1
- Bump to v1.26.1
* Sun Mar 26 2023 Karel Van Hecke <copr@karelvanhecke.com> - 1.25.0-1
- Initial build
