%global upver 7.2.1.202505142326-r

Name:		jgit
Version:	7.2.1.202505142326.r
Release:	2
Summary:	Pure Java implementation of Git
Group:		Development/Java
License:	BSD-3-Clause
URL:		https://github.com/eclipse-jgit/jgit
# Tag v7.2.1.202505142326-r. The archive is Java source. RPM Version
# cannot contain the upstream hyphen. The POMs keep that hyphenated
# string. createrepo stores the hyphen as the release, so these dotted
# provides are the versions the Gradle comparison can match.
Provides:	mvn(org.eclipse.jgit:org.eclipse.jgit) = 7.2.1.202505142326.r
Provides:	mvn(org.eclipse.jgit:org.eclipse.jgit.ssh.apache) = 7.2.1.202505142326.r
Provides:	mvn(org.eclipse.jgit:org.eclipse.jgit.ssh.apache.agent) = 7.2.1.202505142326.r
Source0:	https://github.com/eclipse-jgit/jgit/archive/refs/tags/v%{upver}.tar.gz#/jgit-%{upver}.tar.gz

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	javapackages-filesystem
BuildRequires:	mvn(com.googlecode.javaewah:JavaEWAH) = 1.2.3
BuildRequires:	mvn(org.slf4j:slf4j-api) = 2.0.17
BuildRequires:	mvn(commons-codec:commons-codec) = 1.18.0
BuildRequires:	mvn(org.apache.sshd:sshd-osgi) = 2.15.0
BuildRequires:	mvn(org.apache.sshd:sshd-sftp) = 2.15.0
BuildRequires:	mvn(net.java.dev.jna:jna) = 5.17.0
BuildRequires:	mvn(net.java.dev.jna:jna-platform) = 5.17.0
Requires:	mvn(com.googlecode.javaewah:JavaEWAH) = 1.2.3
Requires:	mvn(org.slf4j:slf4j-api) = 2.0.17
Requires:	mvn(commons-codec:commons-codec) = 1.18.0
Requires:	mvn(org.apache.sshd:sshd-osgi) = 2.15.0
Requires:	mvn(org.apache.sshd:sshd-sftp) = 2.15.0
Requires:	mvn(net.java.dev.jna:jna) = 5.17.0
Requires:	mvn(net.java.dev.jna:jna-platform) = 5.17.0

%description
Eclipse JGit %{upver}: the core library, the Apache MINA sshd session
factory, and the built-in ssh-agent connector. Gradle 9.9.1 strictly
pins those three artifacts. They are compiled with javac. The command
line, HTTP, LFS, GPG, and JSch modules are not built.

%prep
%autosetup -n jgit-%{upver}
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete

%build
set -eo pipefail
CPCORE=%{_javadir}/JavaEWAH.jar:%{_javadir}/slf4j-api.jar:%{_javadir}/commons-codec-1.18.0.jar
find org.eclipse.jgit/src -name '*.java' > core.list
test "$(wc -l < core.list)" -eq 941
mkdir -p core-classes
javac --release 17 -encoding UTF-8 -Xlint:-options -cp "$CPCORE" -d core-classes @core.list
/bin/cp -a org.eclipse.jgit/resources/. core-classes/
cat > core.mf << 'EOF'
Manifest-Version: 1.0
Automatic-Module-Name: org.eclipse.jgit

EOF
jar cfm org.eclipse.jgit.jar core.mf -C core-classes .
jar i org.eclipse.jgit.jar
javap -verbose -cp org.eclipse.jgit.jar org.eclipse.jgit.api.Git | grep -F 'major version: 61'

CPSSH=org.eclipse.jgit.jar:%{_javadir}/sshd-osgi.jar:%{_javadir}/sshd-sftp.jar:%{_javadir}/slf4j-api.jar
find org.eclipse.jgit.ssh.apache/src -name '*.java' > ssh.list
test "$(wc -l < ssh.list)" -eq 69
mkdir -p ssh-classes
javac --release 17 -encoding UTF-8 -Xlint:-options -cp "$CPSSH" -d ssh-classes @ssh.list
/bin/cp -a org.eclipse.jgit.ssh.apache/resources/. ssh-classes/
cat > ssh.mf << 'EOF'
Manifest-Version: 1.0
Automatic-Module-Name: org.eclipse.jgit.ssh.apache

EOF
jar cfm org.eclipse.jgit.ssh.apache.jar ssh.mf -C ssh-classes .
jar i org.eclipse.jgit.ssh.apache.jar
javap -verbose -cp org.eclipse.jgit.ssh.apache.jar org.eclipse.jgit.transport.sshd.SshdSessionFactory | grep -F 'major version: 61'

CPAGENT=org.eclipse.jgit.jar:org.eclipse.jgit.ssh.apache.jar:%{_javadir}/sshd-osgi.jar:%{_javadir}/jna-5.17.0.jar:%{_javadir}/jna-platform-5.17.0.jar:%{_javadir}/slf4j-api.jar
find org.eclipse.jgit.ssh.apache.agent/src -name '*.java' > agent.list
test "$(wc -l < agent.list)" -eq 9
mkdir -p agent-classes
javac --release 17 -encoding UTF-8 -Xlint:-options -cp "$CPAGENT" -d agent-classes @agent.list
/bin/cp -a org.eclipse.jgit.ssh.apache.agent/resources/. agent-classes/
cat > agent.mf << 'EOF'
Manifest-Version: 1.0
Automatic-Module-Name: org.eclipse.jgit.ssh.apache.agent

EOF
jar cfm org.eclipse.jgit.ssh.apache.agent.jar agent.mf -C agent-classes .
jar i org.eclipse.jgit.ssh.apache.agent.jar
javap -verbose -cp org.eclipse.jgit.ssh.apache.agent.jar org.eclipse.jgit.internal.transport.sshd.agent.connector.Factory | grep -F 'major version: 61'

cat > org.eclipse.jgit.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.eclipse.jgit</groupId>
  <artifactId>org.eclipse.jgit</artifactId>
  <version>%{upver}</version>
  <name>JGit Core</name>
  <description>Pure Java implementation of Git</description>
  <licenses>
    <license>
      <name>BSD-3-Clause</name>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>com.googlecode.javaewah</groupId>
      <artifactId>JavaEWAH</artifactId>
      <version>1.2.3</version>
    </dependency>
    <dependency>
      <groupId>org.slf4j</groupId>
      <artifactId>slf4j-api</artifactId>
      <version>2.0.17</version>
    </dependency>
    <dependency>
      <groupId>commons-codec</groupId>
      <artifactId>commons-codec</artifactId>
      <version>1.18.0</version>
    </dependency>
  </dependencies>
</project>
EOF

cat > org.eclipse.jgit.ssh.apache.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.eclipse.jgit</groupId>
  <artifactId>org.eclipse.jgit.ssh.apache</artifactId>
  <version>%{upver}</version>
  <name>JGit Apache SSH</name>
  <description>JGit SSH session factory based on Apache MINA sshd</description>
  <licenses>
    <license>
      <name>BSD-3-Clause</name>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>org.eclipse.jgit</groupId>
      <artifactId>org.eclipse.jgit</artifactId>
      <version>%{upver}</version>
    </dependency>
    <dependency>
      <groupId>org.apache.sshd</groupId>
      <artifactId>sshd-osgi</artifactId>
      <version>2.15.0</version>
    </dependency>
    <dependency>
      <groupId>org.apache.sshd</groupId>
      <artifactId>sshd-sftp</artifactId>
      <version>2.15.0</version>
    </dependency>
    <dependency>
      <groupId>org.slf4j</groupId>
      <artifactId>slf4j-api</artifactId>
      <version>2.0.17</version>
    </dependency>
  </dependencies>
</project>
EOF

cat > org.eclipse.jgit.ssh.apache.agent.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.eclipse.jgit</groupId>
  <artifactId>org.eclipse.jgit.ssh.apache.agent</artifactId>
  <version>%{upver}</version>
  <name>JGit Apache SSH agent</name>
  <description>Built-in ssh-agent connector for the JGit Apache SSH factory</description>
  <licenses>
    <license>
      <name>BSD-3-Clause</name>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>org.eclipse.jgit</groupId>
      <artifactId>org.eclipse.jgit</artifactId>
      <version>%{upver}</version>
    </dependency>
    <dependency>
      <groupId>org.eclipse.jgit</groupId>
      <artifactId>org.eclipse.jgit.ssh.apache</artifactId>
      <version>%{upver}</version>
    </dependency>
    <dependency>
      <groupId>net.java.dev.jna</groupId>
      <artifactId>jna</artifactId>
      <version>5.17.0</version>
    </dependency>
    <dependency>
      <groupId>net.java.dev.jna</groupId>
      <artifactId>jna-platform</artifactId>
      <version>5.17.0</version>
    </dependency>
    <dependency>
      <groupId>org.slf4j</groupId>
      <artifactId>slf4j-api</artifactId>
      <version>2.0.17</version>
    </dependency>
  </dependencies>
</project>
EOF

%install
sysjar install --buildroot %{buildroot} \
	--artifact org.eclipse.jgit.pom:org.eclipse.jgit.jar \
	--file-name org.eclipse.jgit \
	--filelist .mfiles
sysjar install --buildroot %{buildroot} \
	--artifact org.eclipse.jgit.ssh.apache.pom:org.eclipse.jgit.ssh.apache.jar \
	--file-name org.eclipse.jgit.ssh.apache \
	--filelist .mfiles-ssh
sysjar install --buildroot %{buildroot} \
	--artifact org.eclipse.jgit.ssh.apache.agent.pom:org.eclipse.jgit.ssh.apache.agent.jar \
	--file-name org.eclipse.jgit.ssh.apache.agent \
	--filelist .mfiles-agent
cat .mfiles-ssh .mfiles-agent >> .mfiles
sort -u -o .mfiles .mfiles

%check
set -eo pipefail
CORE=%{buildroot}%{_javadir}/org.eclipse.jgit.jar
SSH=%{buildroot}%{_javadir}/org.eclipse.jgit.ssh.apache.jar
AGENT=%{buildroot}%{_javadir}/org.eclipse.jgit.ssh.apache.agent.jar
test -f "$CORE"
test -f "$SSH"
test -f "$AGENT"
mkdir -p check
cat > check/Smoke.java << 'EOF'
import java.nio.file.Files;
import java.nio.file.Path;
import org.eclipse.jgit.api.Git;
import org.eclipse.jgit.lib.PersonIdent;
import org.eclipse.jgit.revwalk.RevCommit;
import org.eclipse.jgit.transport.sshd.SshdSessionFactory;
import org.eclipse.jgit.internal.transport.sshd.agent.connector.Factory;
public class Smoke {
	public static void main(String[] args) throws Exception {
		Path dir = Files.createTempDirectory("jgit-smoke");
		try (Git git = Git.init().setDirectory(dir.toFile()).setInitialBranch("master").call()) {
			Files.writeString(dir.resolve("gradle.txt"), "gradle\n");
			git.add().addFilepattern("gradle.txt").call();
			RevCommit commit = git.commit()
				.setMessage("gradle")
				.setAuthor(new PersonIdent("gradle", "gradle@example.com"))
				.setCommitter(new PersonIdent("gradle", "gradle@example.com"))
				.call();
			if (!"gradle".equals(commit.getShortMessage())) {
				throw new RuntimeException(commit.getShortMessage());
			}
			if (!"master".equals(git.getRepository().getBranch())) {
				throw new RuntimeException(git.getRepository().getBranch());
			}
			System.out.println("jgit_ok " + commit.getShortMessage() + " " + git.getRepository().getBranch());
		}
		SshdSessionFactory ssh = new SshdSessionFactory();
		try {
			if (!"mina-sshd".equals(ssh.getType())) {
				throw new RuntimeException(ssh.getType());
			}
			System.out.println("jgitssh_ok " + ssh.getType());
		} finally {
			ssh.close();
		}
		Factory agent = new Factory();
		if (!agent.isSupported() || !"jgit-builtin".equals(agent.getName())) {
			throw new RuntimeException(agent.getName());
		}
		System.out.println("jgitagent_ok " + agent.getName() + " " + agent.isSupported());
	}
}
EOF
CP="$CORE:$SSH:$AGENT:%{_javadir}/JavaEWAH.jar:%{_javadir}/slf4j-api.jar:%{_javadir}/commons-codec-1.18.0.jar:%{_javadir}/sshd-osgi.jar:%{_javadir}/sshd-sftp.jar:%{_javadir}/jna-5.17.0.jar:%{_javadir}/jna-platform-5.17.0.jar"
javac --release 17 -encoding UTF-8 -Xlint:-options -cp "$CP" -d check check/Smoke.java
java -cp "check:$CP" Smoke > check/out.txt
cat check/out.txt
grep -F -q 'jgit_ok gradle master' check/out.txt
grep -F -q 'jgitssh_ok mina-sshd' check/out.txt
grep -F -q 'jgitagent_ok jgit-builtin true' check/out.txt

%files -f .mfiles
%license LICENSE
%doc README.md
