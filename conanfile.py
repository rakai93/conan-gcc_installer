import os
from conans import ConanFile, AutoToolsBuildEnvironment
from conans.client import tools


class GccInstallerConan(ConanFile):
    name = "gcc_installer"
    version = "8.1.0"
    license = "TDB"
    url = "https://gcc.gnu.org/"
    settings = "os_build", "arch_build"
    build_policy = "missing"
    description = "GCC installer. Useful as a build_requires."
    no_copy_source = True

    @property
    def source_url(self):
        return f"https://ftp.gnu.org/gnu/gcc/gcc-{self.version}/gcc-{self.version}.tar.xz"

    @property
    def gcc_folder(self):
        return f"gcc-{self.version}"

    def source(self):
        self.output.info(f"Downloading GCC sources from {self.source_url}")
        tools.get(self.source_url)

        self.output.info("Downloading prerequisites")
        self.run(f"cd {self.gcc_folder} && ./contrib/download_prerequisites")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)

        configure_args = [
            "--disable-multilib",
            "--enable-plugin",
            "--enable-languages=c,c++,lto",
            # manually specify libexecdir, otherwise it points to bin/ and creates naming conflicts
            "--libexecdir=${prefix}/libexec"
        ]
        if self.settings.arch_build == "armv7":
            configure_args.append("--with-float=hard")

        autotools.configure(configure_dir=os.path.join(self.source_folder, self.gcc_folder),
                            args=configure_args)
        autotools.make()

    def package(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.install()

    def package_info(self):
        # expose gcc
        self.env_info.path.append(os.path.join(self.package_folder, "bin"))
        self.env_info.CXX = os.path.join(self.package_folder, "bin", "g++")
        self.env_info.CC = os.path.join(self.package_folder, "bin", "gcc")

        # overwrite include path
        include_root = os.path.join(self.package_folder, "include", "c++", self.version)
        self.cpp_info.includedirs = [
            include_root,
            os.path.join(include_root, f"{self.settings.arch_build}-pc-{str(self.settings.os_build).lower()}-gnu")
        ]
