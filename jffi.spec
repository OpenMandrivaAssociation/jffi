%{?_javapackages_macros:%_javapackages_macros}
%define _enable_debug_packages %{nil}
%define debug_package %{nil}
%define _disable_lto 1

%global cluster jnr
%global sover 1.2

Name:           jffi
Version:        1.2.9
Release:        1.1
Summary:        Java Foreign Function Interface
Group:		Development/Java
License:        LGPLv3+ or ASL 2.0
URL:            http://github.com/jnr/jffi
Source0:        https://github.com/%{cluster}/%{name}/archive/%{version}.zip
Patch0:         jffi-fix-dependencies-in-build-xml.patch
Patch1:         jffi-add-built-jar-to-test-classpath.patch
Patch2:         jffi-fix-compilation-flags.patch

BuildRequires:  maven-local
BuildRequires:  ffi-devel
BuildRequires:  ant
BuildRequires:  junit

%description
An optimized Java interface to libffi.

%package native
Summary:        %{name} JAR with native bits

%description native
This package contains %{name} JAR with native bits.

%package javadoc
Summary:        Javadoc for %{name}
BuildArch:      noarch

%description javadoc
This package contains the API documentation for %{name}.


%prep
%setup -q
%patch0
%patch1
%patch2

# ppc{,64} fix
# https://bugzilla.redhat.com/show_bug.cgi?id=561448#c9
sed -i.cpu -e '/m\$(MODEL)/d' jni/GNUmakefile libtest/GNUmakefile

# remove uneccessary directories
rm -rf archive/* jni/libffi/ jni/win32/ lib/CopyLibs/ lib/junit*

find ./ -name '*.jar' -exec rm -f '{}' \; 
find ./ -name '*.class' -exec rm -f '{}' \; 

build-jar-repository -s -p lib/ junit

%mvn_package 'com.github.jnr:jffi::native:' native
%mvn_file ':{*}' %{name}/@1 @1

%build
# ant will produce JAR with native bits
ant jar build-native -Duse.system.libffi=1

# maven will look for JAR with native bits in archive/
cp -p dist/jffi-*-Linux.jar archive/

%mvn_build

%install
%mvn_install

# install *.so
install -dm 755 %{buildroot}%{_libdir}/%{name}
cp -rp target/jni/* %{buildroot}%{_libdir}/%{name}/
# create version-less symlink for .so file
sofile=`find %{buildroot}%{_libdir}/%{name} -name lib%{name}-%{sover}.so`
ln -sr ${sofile} `dirname ${sofile}`/lib%{name}.so

%check
# skip tests on s390 until https://bugzilla.redhat.com/show_bug.cgi?id=1084914 is resolved
%if 0
%ifnarch s390
# don't fail on unused parameters... (TODO: send patch upstream)
sed -i 's|-Werror||' libtest/GNUmakefile
ant -Duse.system.libffi=1 test
%endif
%endif

%files -f .mfiles
%doc COPYING.GPL COPYING.LESSER LICENSE

%files native -f .mfiles-native
%{_libdir}/%{name}
%doc COPYING.GPL COPYING.LESSER LICENSE

%files javadoc -f .mfiles-javadoc
%doc COPYING.GPL COPYING.LESSER LICENSE

%changelog
* Tue May 5 2015 Alexander Kurtakov <akurtako@redhat.com> 1.2.9-1
- Update to upstream 1.2.9.

* Thu Apr 30 2015 Alexander Kurtakov <akurtako@redhat.com> 1.2.8-1
- Update to upstream 1.2.8.

* Fri Feb 20 2015 Michal Srb <msrb@redhat.com> - 1.2.7-5
- Install version-less symlink for .so file

* Fri Feb 20 2015 Michal Srb <msrb@redhat.com> - 1.2.7-4
- Fix rpmlint warnings

* Fri Feb 20 2015 Michal Srb <msrb@redhat.com> - 1.2.7-3
- Install *.so file to %%{_libdir}/%%{name}/

* Tue Feb 17 2015 Michal Srb <msrb@redhat.com> - 1.2.7-2
- Build jffi-native
- Introduce javadoc subpackage

* Fri Dec 05 2014 Mo Morsi <mmorsi@redhat.com> - 1.2.7-1
- Update to JFFI 1.2.7

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.6-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jun 12 2014 Alexander Kurtakov <akurtako@redhat.com> 1.2.6-7
- Fix FTBFS.

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.6-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Apr 07 2014 Dan Horák <dan[at]danny.cz> - 1.2.6-5
- skip tests on s390 until https://bugzilla.redhat.com/show_bug.cgi?id=1084914 is resolved

* Fri Mar 28 2014 Michael Simacek <msimacek@redhat.com> - 1.2.6-4
- Use Requires: java-headless rebuild (#1067528)

* Sun Aug 11 2013 Mat Booth <fedora@matbooth.co.uk> - 1.2.6-3
- Remove BR on ant-nodeps, fixes FTBFS rhbz #992622

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Feb 05 2013 Bohuslav Kabrda <bkabrda@redhat.com> - 1.2.6-1
- Updated to version 1.2.6.

* Wed Dec 19 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.0.10-4
- revbump after jnidir change

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.10-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Aug 02 2011  Mo Morsi <mmorsi@redhat.com> - 1.0.10-1
- Updated to most recent upstream release

* Wed Jun 01 2011  Mo Morsi <mmorsi@redhat.com> - 1.0.9-1
- Updated to most recent upstream release

* Mon Oct 25 2010  <mmorsi@redhat.com> - 1.0.2-1
- Updated to most recent upstream release

* Wed Apr 14 2010  <mmorsi@redhat.com> - 0.6.5-4
- added Mamoru Tasaka's fix for ppc{,64} to prep

* Mon Mar 08 2010  <mmorsi@redhat.com> - 0.6.5-3
- fixes to jffi from feedback
- don't strip debuginfo, remove extraneous executable bits,

* Tue Feb 23 2010  <mmorsi@redhat.com> - 0.6.5-2
- fixes to jffi compilation process
- fixes to spec to conform to package guidelines

* Wed Feb 17 2010  <mmorsi@redhat.com> - 0.6.5-1
- bumped version
- fixed package to comply to fedora guidelines

* Tue Jan 19 2010  <mmorsi@redhat.com> - 0.6.2-1
- Initial build.

