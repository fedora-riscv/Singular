%global singulardir	%{_libdir}/Singular
%global upstreamver	3-1-6

%if 0%{?fedora} > 18
%define ntl6 1
%endif

# If a library used by both polymake and Singular is updated, neither can be
# rebuilt, because each BRs the other and both are linked against the old
# version of the library.  Use this to rebuild Singular without polymake
# support, rebuild polymake, then build Singular again with polymake support.
%bcond_without polymake

Name:		Singular
Version:	%(tr - . <<<%{upstreamver})
Release:	8%{?dist}
Summary:	Computer Algebra System for polynomial computations
Group:		Applications/Engineering
License:	BSD and LGPLv2+ and GPLv2+
Source0:	http://www.mathematik.uni-kl.de/ftp/pub/Math/Singular/SOURCES/%{upstreamver}/%{name}-%{upstreamver}.tar.gz
# TEMPORARY: Remove this once Singular ships an updated version
Source1:	normaliz.lib
URL:		http://www.singular.uni-kl.de/
BuildRequires:	cddlib-devel
BuildRequires:	emacs
BuildRequires:	flex
BuildRequires:	flint-devel
BuildRequires:	gmp-devel
BuildRequires:	libxml2-devel
BuildRequires:	ncurses-devel
BuildRequires:	ntl-devel%{?ntl6: >= 6.0}
%if %{with polymake}
BuildRequires:	polymake-devel
%endif
BuildRequires:	readline-devel
# Need uudecode for documentation images in tarball
BuildRequires:	sharutils
BuildRequires:	texinfo
BuildRequires:	tex(latex)
BuildRequires:	zlib-devel
Requires:	factory-gftables = %{version}-%{release}
Requires:	less
Requires:	surf-geometry

# Use destdir in install targets
Patch1:		Singular-destdir.patch
# Find headers in source tree
Patch2:		Singular-headers.patch
# Find and link to generated libraries
Patch3:		Singular-link.patch
# Do not attempt to load non existing modules, do not even run
# the binary in DESTDIR when building the documentation
Patch4:		Singular-doc.patch
# Correct koji error:
# ** ERROR: No build ID note found in /builddir/build/BUILDROOT/Singular-3.1.3-1.fc16.x86_64/usr/lib64/Singular/dbmsr.so
Patch5:		Singular-builddid.patch
# Correct undefined symbols in libsingular
# This patch removes a hack to avoid duplicated symbols in tesths.cc
# when calling mp_set_memory_functions, what is a really a bad idea on
# a shared library.
Patch6:		Singular-undefined.patch

# Add missing #include directives in the semaphore code
Patch11:	Singular-semaphore.patch
# Adapt to new template code in NTL 6
Patch12:	Singular-ntl6.patch
# Support ARM and S390(x) architectures
Patch13:	Singular-arches.patch
# Adapt to changes in flint 2.4
Patch14:	Singular-flint24.patch

## Macaulay2 patches
Patch20: Singular-M2_factory.patch
Patch21: Singular-M2_memutil_debuggging.patch
Patch22: Singular-M2_libfac.patch

%description
Singular is a computer algebra system for polynomial computations, with
special emphasis on commutative and non-commutative algebra, algebraic
geometry, and singularity theory. It is free and open-source under the
GNU General Public Licence.

%package	devel
Summary:	Singular development files
Group:		Development/Libraries
Requires:	factory-devel
Requires:	libfac-devel
Requires:	%{name}%{?_isa} = %{version}-%{release}

%description	devel
This package contains the Singular development files.

%package	-n factory-devel
Summary:	C++ class library for multivariate polynomial data
Group:		Development/Libraries
Requires:	gmp-devel
Obsoletes:	factory-static < %{version}-%{release}
Provides:	factory-static = %{version}-%{release}

%description	-n factory-devel 
Factory is a C++ class library that implements a recursive representation
of multivariate polynomial data.

%package	-n factory-gftables
Summary:	Factory addition tables
Group:		Applications/Engineering
BuildArch: noarch

%description -n	factory-gftables
Factory uses addition tables to calculate in GF(p^n) in an efficient way.


%package	-n libfac-devel
Summary:	An extension to Singular-factory
Group:		Development/Libraries
Obsoletes:	libfac-static < %{version}-%{release}
Provides:	libfac-static = %{version}-%{release}

%description	-n libfac-devel
Singular-libfac is an extension to Singular-factory which implements
factorization of polynomials over finite fields and algorithms for
manipulation of polynomial ideals via the characteristic set methods
(e.g., calculating the characteristic set and the irreducible
characteristic series).

%package	examples
Summary:	Singular example files
Group:		Applications/Engineering
Requires:	%{name}%{?_isa} = %{version}-%{release}

%description	examples
This package contains the Singular example files.

%package	doc
Summary:	Singular documentation files
Group:		Applications/Engineering
Requires:	%{name}%{?_isa} = %{version}-%{release}

%description	doc
This package contains the Singular documentation files.

%package	surfex
Summary:	Singular java interface
Group:		Applications/Engineering
Requires:	java
Requires:	%{name}%{?_isa} = %{version}-%{release}

%description	surfex
This package contains the Singular java interface.

%package	emacs
Summary:	Emacs mode for Singular
Group:		Applications/Engineering
Requires:	emacs-common
Requires:	%{name}%{?_isa} = %{version}-%{release}

%description	emacs
Emacs mode for Singular.

%prep
%setup -q -n %{name}-%{upstreamver}
%patch1 -p1 -b .destdir
%patch2 -p1 -b .headers
%patch3 -p1 -b .link
%patch4 -p1
%patch5 -p1 -b .builddid
%patch6 -p1 -b .undefined

%patch11 -p1
%if 0%{?ntl6:1}
%patch12 -p1
%endif
%patch13 -p1
%patch14 -p1 -b .flint24

#patch20 -p1 -b .M2_factory
#patch21 -p1 -b .M2_memutil_debuggging
#patch22 -p1 -b .M2_libfac

sed -i -e "s|gftabledir=.*|gftabledir='%{singulardir}/LIB/gftables'|"	\
    -e "s|explicit_gftabledir=.*|explicit_gftabledir='%{singulardir}/LIB/gftables'|" \
    factory/configure.in factory/configure

# Build the debug libfactory with the right CFLAGS
sed -i 's/\($(CPPFLAGS)\) \($(FLINT_CFLAGS)\)/\1 $(CFLAGS) \2/' \
    factory/GNUmakefile.in

# Build the debug kernel with the right CFLAGS
sed -ri 's/(C(XX)?FLAGS)(.*= )-g/\1\3$(\1)/' kernel/Makefile.in

# Build libparse with the right CFLAGS
sed -r 's/(\$\{CXX\})[[:blank:]]+(-O2[[:blank:]]+)?(\$\{CPPFLAGS\})/\1 $\{CXXFLAGS\} \3/' \
    -i Singular/Makefile.in

# Fix permissions
sed -i 's,${INSTALL_PROGRAM} libsingular.h,${INSTALL_DATA} libsingular.h,' \
    Singular/Makefile.in

# Force use of system ntl
rm -fr ntl

# Adapt to the Fedora flint package
mkdir -p flint/include
ln -s %{_includedir}/flint flint/include/flint
ln -s %{_libdir} flint/lib
sed -i 's/lmpir/lgmp/' factory/configure Singular/configure

# Unbreak the (call)gfanlib/callpolymake installs
sed -i '/^install:/iinstall-libsingular:\n' \
    gfanlib/Makefile.in callgfanlib/Makefile.in
sed -e '/^install /iinstall-libsingular:\n' \
    -e 's/mkdir/mkdir -p/' \
    -i callpolymake/Makefile.in
sed -ri 's/@(prefix|exec_prefix|libdir|includedir)@/$(DESTDIR)&/g' \
    gfanlib/Makefile.in

# Fix the default paths
sed -e 's/"S_UNAME"/Singular/' \
    -e 's/"S_UNAME/Singular"/' \
    -e 's,%b/\.\.,%b,' \
    -e 's,S_ROOT_DIR,"%{_libdir}",' \
    -i.orig kernel/feResource.cc
touch -r kernel/feResource.cc.orig kernel/feResource.cc

%if 0%{?fedora} > 20
# TEMPORARY: Remove this once Singular ships an updated version
cp -p %{SOURCE1} Singular/LIB
%endif

%build
export CFLAGS="%{optflags} -fPIC -fsigned-char -I%{_includedir}/cddlib -I%{_includedir}/flint"
export CXXFLAGS=$CFLAGS
export LDFLAGS="$RPM_LD_FLAGS -Wl,--as-needed -L$PWD/gfanlib"
export LIBS="-lpthread -ldl"

# build components in specific order to not need to build & install
# in a single make command
%configure \
	--bindir=%{singulardir} \
	--with-apint=gmp \
	--with-flint=$PWD/flint \
	--with-gmp=%{_prefix} \
	--with-ntl=%{_prefix} \
	--with-NTL \
	--without-MP \
	--without-lex \
	--without-bison \
	--without-Boost \
	--enable-gmp=%{_prefix} \
	--enable-Singular \
	--enable-factory \
	--enable-libfac \
	--enable-IntegerProgramming \
	--enable-gfanlib \
%if %{with polymake}
	--enable-polymake \
%endif
	--disable-doc \
	--with-malloc=system
# remove bogus -L/usr/kernel from linker command line and
# do not put standard library in linker command line to avoid
# linking with a system wide libsingcf or libfacf
sed -i 's|-L%{_prefix}/kernel||g;s|-L%{_libdir}||g' Singular/Makefile
make %{?_smp_mflags} Singular
# factory needs omalloc built
make %{?_smp_mflags} -C omalloc
%if %{with polymake}
# polymake interface needs gfanlib built
make %{?_smp_mflags} -C gfanlib
%endif

pushd factory
%configure \
	--bindir=%{singulardir} \
	--includedir=%{_includedir}/factory \
	--with-apint=gmp \
	--with-flint=$PWD/../flint \
	--with-gmp=%{_prefix} \
	--with-ntl=%{_prefix} \
	--with-NTL \
	--with-Singular \
	--enable-gmp=%{_prefix}
    make %{?_smp_mflags}
popd

# kernel needs factory built
make %{?_smp_mflags} -C kernel

# libfac needs factory built
pushd libfac
%configure \
	--bindir=%{singulardir} \
	--with-apint=gmp \
	--with-flint=$PWD/../flint \
	--with-gmp=%{_prefix} \
	--with-ntl=%{_prefix} \
	--with-NTL \
	--enable-factory \
	--enable-libfac \
	--enable-omalloc \
	--enable-gmp=%{_prefix}
    make %{?_smp_mflags}
    # not built by default
    make libfac.a
popd

# target required to rebuild documentation
make %{?_smp_mflags} -C Singular libparse

%install
make \
	DESTDIR=$RPM_BUILD_ROOT \
	install_prefix=$RPM_BUILD_ROOT%{singulardir} \
	slibdir=%{singulardir}/LIB \
	install \
	install-libsingular \
	install-sharedist

# dup gftables data
GF_DIR=%{_datadir}/factory/gftables
mkdir -p $RPM_BUILD_ROOT${GF_DIR}
pushd $RPM_BUILD_ROOT%{singulardir}/LIB/gftables
for file in * ; do
 new_file="gftable.$(head -2 ${file} | tail -1 | cut -d' ' -f1,2 | sed -e 's| |.|')"
 ## absolute
 #mv ${file} $RPM_BUILD_ROOT${GF_DIR}/${new_file}
 #ln -s ${GF_DIR}/${new_file} ${file}
 ## relative
 mv ${file} ../../../../share/factory/gftables/${new_file}
 ln -s ../../../../share/factory/gftables/${new_file} ${file}
done
popd

# does not need to be in top directory
mkdir $RPM_BUILD_ROOT%{_includedir}/gfanlib
mv $RPM_BUILD_ROOT%{_includedir}/gfanlib*.h \
    $RPM_BUILD_ROOT%{_includedir}/gfanlib
mv $RPM_BUILD_ROOT%{_includedir}/{my,om}limits.h \
    $RPM_BUILD_ROOT%{_includedir}/singular

# also installed in libdir
rm -f $RPM_BUILD_ROOT%{_bindir}/*.so
rm -f $RPM_BUILD_ROOT%{singulardir}/libsingular.so
rm -f $RPM_BUILD_ROOT%{singulardir}/polymake.so

# already linked to libsingular.so; do not distribute static libraries
# or just compiled objects.
rm -f $RPM_BUILD_ROOT%{_libdir}/*.a $RPM_BUILD_ROOT%{_libdir}/*.o

# avoid poluting libdir with dynamic modules
pushd $RPM_BUILD_ROOT%{_libdir}
    mkdir -p Singular
    mv dbmsr.so p_Procs*.so Singular
popd

# create a script also setting SINGULARPATH
mkdir -p $RPM_BUILD_ROOT%{_bindir}
cat > $RPM_BUILD_ROOT%{_bindir}/Singular << EOF
#!/bin/sh

module load surf-geometry-%{_arch}
SINGULARPATH=%{singulardir} %{singulardir}/Singular-%{upstreamver} "\$@"
EOF
chmod +x $RPM_BUILD_ROOT%{_bindir}/Singular

# TSingular
cat > $RPM_BUILD_ROOT%{_bindir}/TSingular << EOF
#!/bin/sh

module load surf-geometry-%{_arch}
%{singulardir}/TSingular --singular %{_bindir}/Singular "\$@"
EOF
chmod +x $RPM_BUILD_ROOT%{_bindir}/TSingular

# remove some wrong executable permissions
chmod 644 $RPM_BUILD_ROOT%{singulardir}/LIB/*.lib

# surfex
cat > $RPM_BUILD_ROOT%{_bindir}/surfex << EOF
#!/bin/sh

module load surf-geometry-%{_arch}
%{singulardir}/surfex %{singulardir}/LIB/surfex "\$@"
EOF
chmod +x $RPM_BUILD_ROOT%{_bindir}/surfex
mkdir -p $RPM_BUILD_ROOT%{singulardir}/LIB/surfex/doc
install -m644 Singular/LIB/surfex/doc/surfex_doc_linux.pdf \
    $RPM_BUILD_ROOT%{singulardir}/LIB/surfex/doc/surfex_doc_linux.pdf

# referenced in xemacs setup
install -m644 emacs/singular.xpm $RPM_BUILD_ROOT%{_emacs_sitelispdir}/singular

# remove suggested preferences
rm -f $RPM_BUILD_ROOT%{_emacs_sitelispdir}/singular/.emacs-general

# emacs autostart
sed -i "s|<your-singular-emacs-home-directory>|%{_emacs_sitelispdir}/singular|" \
    $RPM_BUILD_ROOT%{_emacs_sitelispdir}/singular/.emacs-singular
mkdir -p $RPM_BUILD_ROOT%{_emacs_sitestartdir}
mv $RPM_BUILD_ROOT%{_emacs_sitelispdir}/singular/.emacs-singular \
     $RPM_BUILD_ROOT%{_emacs_sitestartdir}/singular-init.el

# ESingular
cat > $RPM_BUILD_ROOT%{_bindir}/ESingular << EOF
#!/bin/sh

module load surf-geometry-%{_arch}
export ESINGULAR_EMACS_LOAD=%{_emacs_sitestartdir}/singular-init.el
export ESINGULAR_EMACS_DIR=%{_emacs_sitelispdir}/singular
%{singulardir}/ESingular --singular %{_bindir}/Singular "\$@"
EOF
chmod +x $RPM_BUILD_ROOT%{_bindir}/ESingular

pushd libfac
    make DESTDIR=$RPM_BUILD_ROOT install
    # not installed by default
    install -m 644 libfac.a $RPM_BUILD_ROOT%{_libdir}/libfac.a
popd

pushd factory
    make DESTDIR=$RPM_BUILD_ROOT install
# make a version without singular defined
    make clean
%configure \
	--bindir=%{singulardir} \
	--includedir=%{_includedir}/factory \
	--with-apint=gmp \
	--with-flint=$PWD/../flint \
	--with-gmp=%{_prefix} \
	--with-ntl=%{_prefix} \
	--with-NTL \
	--without-Singular \
	--enable-gmp=%{_prefix}
    # avoid missing "print" symbols not used elsewhere
    make CPPFLAGS="-I%{_includedir}/flint -DNOSTREAMIO=1" %{?_smp_mflags}
    # not built by default
    make libcfmem.a
    # do not run make install again, just install non singular factory files
    install -m 644 libcf.a $RPM_BUILD_ROOT%{_libdir}
    install -m 644 libcfmem.a $RPM_BUILD_ROOT%{_libdir}
popd

# incorrect factory includedir
sed -e 's|<\(cf_gmp.h>\)|<factory/\1|' \
    -i $RPM_BUILD_ROOT%{_includedir}/singular/si_gmp.h

%files
%{_bindir}/Singular
%{_bindir}/TSingular
%doc %{singulardir}/COPYING
%doc %{singulardir}/GPL2
%doc %{singulardir}/GPL3
%doc %{singulardir}/NEWS
%doc %{singulardir}/README
%dir %{singulardir}
%dir %{singulardir}/LIB
%doc %{singulardir}/LIB/COPYING
%{singulardir}/LIB/*.lib
%{singulardir}/LIB/help.cnf
%{singulardir}/LIB/gftables
%{singulardir}/doc
%{singulardir}/info
%{singulardir}/change_cost
%{singulardir}/gen_test
%{singulardir}/libparse
%{singulardir}/LLL
%{singulardir}/Singular*
%{singulardir}/solve_IP
%{singulardir}/toric_ideal
%{singulardir}/TSingular
%{singulardir}/*.so
%{_libdir}/libsingular.so
%if %{with polymake}
%{singulardir}/MOD/
%endif

%files		devel
%{_includedir}/gfanlib
%{_includedir}/libsingular.h
%{_includedir}/omalloc.h
%{_includedir}/singular

%files		-n factory-gftables
%dir %{_datadir}/factory/
%{_datadir}/factory/gftables/

%files		-n factory-devel
%doc factory/ChangeLog
%doc factory/NEWS
%doc factory/README
%{_includedir}/factory
%{_libdir}/libcf.a
%{_libdir}/libcfmem.a
%{_libdir}/libsingcf*.a

%files		-n libfac-devel
%doc libfac/00README
%doc libfac/ChangeLog
%doc libfac/COPYING
%{_includedir}/factor.h
%{_libdir}/libfac.a
%{_libdir}/libsingfac*.a

%files		examples
%{singulardir}/examples

%files		doc
%doc %{singulardir}/html
%doc %{singulardir}/*.html

%files		surfex
%{_bindir}/surfex
%{singulardir}/surfex
%{singulardir}/LIB/surfex

%files		emacs
%{_bindir}/ESingular
%{singulardir}/ESingular
%{_emacs_sitelispdir}/singular
%{_emacs_sitestartdir}/singular-init.el

%changelog
* Tue Oct 28 2014 Jerry James <loganjerry@gmail.com> - 3.1.6-8
- Rebuild for ntl 6.2.1

* Thu Sep 11 2014 Jerry James <loganjerry@gmail.com> - 3.1.6-7
- Rebuild for polymake -2.13-8.git20140811

* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.6-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Tue Jun 17 2014 Jerry James <loganjerry@gmail.com> - 3.1.6-5
- Update Singular-ntl6.patch to instantiate more missing functions

* Fri Jun 06 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.6-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu May 29 2014 Jerry James <loganjerry@gmail.com> - 3.1.6-3
- Rebuild with polymake support
- Fix libsingular.h permissions

* Sun May 18 2014 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 3.1.6-2
- Merge with RFE 3.1.6 update (#1074590)
- Remove patches applied upstream
- Disable polymake to allow interface rebootstrap

* Tue Apr 29 2014 Jerry James <loganjerry@gmail.com> - 3.1.5-14
- Rebuild for polymake-2.13

* Wed Apr  2 2014 Jerry James <loganjerry@gmail.com> - 3.1.5-13
- Rebuild for polymake-2.12-15.svn20140326

* Wed Apr  2 2014 Jerry James <loganjerry@gmail.com> - 3.1.5-12
- Rebuild for NTL 6.1.0
- Fix default paths
- Add ability to rebuild without polymake

* Mon Mar 10 2014 Rex Dieter <rdieter@fedoraproject.org> - 3.1.6-1
- 3.1.6

* Mon Mar 10 2014 Rex Dieter <rdieter@fedoraproject.org> - 3.1.5-11
- fix/workaround char=unsigned char assumptions
- (more) consistently use RPM_OPT_FLAGS
- --with-flint --with-polymake

* Tue Jan 14 2014 Jerry James <loganjerry@gmail.com> - 3.1.5-10
- Update normaliz interface for normaliz 2.8 and later

* Mon Nov 25 2013 Rex Dieter <rdieter@fedoraproject.org> - 3.1.5-9
- ExclusiveArch: %%ix86 x86_64

* Fri Aug 16 2013 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 3.1.5-8
- Correct underlink problem (#991920#c1)

* Thu Aug 01 2013 Rex Dieter <rdieter@fedoraproject.org> - 3.1.5-7
- rebuild

* Tue May 21 2013 Rex Dieter <rdieter@fedoraproject.org> - 3.1.5-6
- factory-gftables.noarch subpkg (#965655)

* Mon May  6 2013 Jerry James <loganjerry@gmail.com> - 3.1.5-5
- Rebuild for ntl 6.0.0
- Fix semaphore code
- Fix underlinked library

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.5-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sun Nov 11 2012 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 3.1.5-3
- Rebuild to have factory include path patch in rawhide package

* Tue Aug 7 2012 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 3.1.5-2
- Do not build conflicts with factory-devel neither libfac-devel (#842407)

* Sat Aug 4 2012 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 3.1.5-1
- Update to Singular 3.1.5, based on sagemath trac ticket #13237
- Remove already applied patches from sagemath Singular spkg
- Rediff Fedora rpm build patches
- Rediff factory and libfac patches for Macaulay2

* Thu Jul 19 2012 Rex Dieter <rdieter@fedoraproject.org> - 3.1.3-8
- macaulay2 patches for libfac/factory
- omit duplicate %%description sections

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.3-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sun Jul 8 2012 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 3.1.3-6
- Update license field to match valid values.
- Provide newer libfac-devel matching Singular version (#819264).
- Provide newer factory-devel matching Singular version (#819264).
- Remove platform specific factoryconf.h file as only platform specific
  contents it has is "#define INT64 long long int" what is not really correct,
  neither completely wrong...

* Sun Jul 1 2012 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 3.1.3-5
- Do not conflict Singular-devel with libfac-devel.

* Sun Jul 1 2012 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 3.1.3-4
- Update license information to match COPYING information.

* Wed May 9 2012 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 3.1.3-3
- Correct unresolved mmInit symbol in libsingular.so.

* Sun May 6 2012 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 3.1.3-2
- Install singular factory headers in singular devel directory.
- Tag singular-doc files as documentation.

* Sat May 5 2012 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 3.1.3-1
- Initial Singular spec.
