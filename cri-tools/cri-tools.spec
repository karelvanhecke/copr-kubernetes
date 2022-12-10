%global goipath github.com/kubernetes-sigs/cri-tools
Version: 1.25.0

%gometa

%global commit0 a12c2d088df8bea138eaeb5a0217d98b6cf93a44
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name: cri-tools
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
export BUILDTAGS="selinux seccomp"
export LDFLAGS="-X %{goipath}/pkg/version.Version=%{version} "
%gobuild -o %{gobuilddir}/bin/crictl %{goipath}/cmd/crictl

%install
install -m 0755 -vd                     %{buildroot}%{_bindir}
install -m 0755 -vp %{gobuilddir}/bin/* %{buildroot}%{_bindir}/

%files
%license LICENSE
%doc CHANGELOG.md CONTRIBUTING.md OWNERS README.md RELEASE.md code-of-conduct.md
%doc docs/{benchmark.md,roadmap.md,validation.md}
%{_bindir}/*

%changelog
* Sat Dec 10 2022 Karel Van Hecke <copr@karelvanhecke.com> - 1.25.0-1
- Initial build
