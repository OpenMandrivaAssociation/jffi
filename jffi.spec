Name:		jffi
Version:	1.4.7
Release:	1
Summary:	Java bindings for libffi
Group:		Development/Java
License:	ASL 2.0 or LGPLv3+
URL:		https://github.com/jnr/jffi
Source0:	https://github.com/jnr/jffi/archive/refs/tags/jffi-%{version}.tar.gz

BuildRequires:	make
BuildRequires:	pkgconfig(libffi)
BuildRequires:	python
BuildSystem:	maven

%description
Java Foreign Function Interface. The JNI library is built from source
against the system libffi. The upstream native jar is a set of prebuilt
binaries and is not packaged.

%prep
%setup -q -n jffi-jffi-%{version}
# archive/ holds prebuilt libjffi for other operating systems.
rm -rf archive
# A linker flag is not a file make can build.
sed -i \
	-e 's/^$(LIBJFFI):.*$(LIBFFI_LIBS)/$(LIBJFFI): $(OBJS)/' \
	-e 's/^$(OBJS) : $(LIBFFI_LIBS)/$(OBJS):/' \
	-e 's/^OFLAGS = -O2 $(JFLAGS)/OFLAGS = -g -O2 $(JFLAGS)/' \
	-e 's/$(STRIP) $@/:/' \
	jni/GNUmakefile
mkdir -p src/main/resources
cat > src/main/resources/boot.properties <<EOF
jffi.boot.library.path=%{_libdir}
EOF
# jnr-parent forces --release 8, which hides sun.misc.Unsafe.
# The compiler toolchain split wants a JDK 8 that we do not build against.
python - <<'PY'
import re
from pathlib import Path
path = Path("pom.xml")
text = path.read_text()
text = re.sub(r"\s*<parent>.*?</parent>", "", text, count=1, flags=re.S)
text = text.replace(
	"<artifactId>jffi</artifactId>",
	"<groupId>com.github.jnr</groupId>\n  <artifactId>jffi</artifactId>",
	1,
)
text = re.sub(
	r"\s*<plugin>\s*<artifactId>maven-compiler-plugin</artifactId>.*?</plugin>",
	"",
	text,
	count=1,
	flags=re.S,
)
text = re.sub(
	r"\s*<plugin>\s*<artifactId>maven-javadoc-plugin</artifactId>.*?</plugin>",
	"",
	text,
	count=1,
	flags=re.S,
)
text = re.sub(
	r"\s*<plugin>\s*<groupId>org\.apache\.felix</groupId>\s*<artifactId>maven-bundle-plugin</artifactId>.*?</plugin>",
	"",
	text,
	count=1,
	flags=re.S,
)
text = re.sub(
	r"\s*<plugin>\s*<groupId>org\.apache\.maven\.plugins</groupId>\s*<artifactId>maven-assembly-plugin</artifactId>.*?</plugin>",
	"",
	text,
	count=1,
	flags=re.S,
)
text = re.sub(
	r"\s*<execution>\s*<phase>process-test-resources</phase>.*?</execution>",
	"",
	text,
	count=1,
	flags=re.S,
)
if "project.build.sourceEncoding" not in text:
	text = text.replace(
		"<properties>",
		"<properties>\n    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>",
		1,
	)
path.write_text(text)
PY

%build -a
# version.xml is the JNI ABI (libjffi-1.2), not the Maven release.
major=$(sed -n 's/.*jffi.version.major" value="\([0-9]*\)".*/\1/p' version.xml)
minor=$(sed -n 's/.*jffi.version.minor" value="\([0-9]*\)".*/\1/p' version.xml)
test -n "$major" -a -n "$minor"
mkdir -p build/jni
"$JAVA_HOME/bin/javac" -h build/jni -d build/jni-classes -classpath target/classes -implicit:none \
	src/main/java/com/kenai/jffi/Foreign.java \
	src/main/java/com/kenai/jffi/ObjectBuffer.java \
	target/java/com/kenai/jffi/Version.java
make -f jni/GNUmakefile \
	JAVA_HOME="$JAVA_HOME" \
	SRC_DIR="$PWD/jni" \
	JNI_DIR="$PWD/jni" \
	BUILD_DIR="$PWD/build/jni" \
	VERSION="$major.$minor" \
	USE_SYSTEM_LIBFFI=1

%install -a
major=$(sed -n 's/.*jffi.version.major" value="\([0-9]*\)".*/\1/p' version.xml)
minor=$(sed -n 's/.*jffi.version.minor" value="\([0-9]*\)".*/\1/p' version.xml)
install -D -p -m 755 "build/jni/libjffi-${major}.${minor}.so" "%{buildroot}%{_libdir}/libjffi-${major}.${minor}.so"

%files -f .mfiles
%{_libdir}/libjffi-*.so
%doc LICENSE README.md
