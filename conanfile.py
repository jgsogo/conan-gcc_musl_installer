import os
import shutil
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class HelperDependency(object):
    name = None
    version = None
    _tar_ext = None
    _url = None

    def __init__(self, version, output):
        self.version = version
        self.output = output

    def source(self):
        kwargs = {'n': self.name, 'v': self.version, 'e': self._tar_ext}
        if not os.path.exists("{n}-{v}".format_map(kwargs)):
            self.output.info("Download {n}".format_map(kwargs))
            url = self._url.format_map(kwargs)
            sha1 = os.path.join("musl-cross-make", "hashes", "{n}-{v}.{e}.sha1".format_map(kwargs))
            sha1 = tools.load(sha1).split(" ", 1)[0]
            tools.get(url, sha1=sha1)

            # Patch
            self.output.info("Apply patches to {n}".format_map(kwargs))
            patch_dir = os.path.abspath(os.path.join("musl-cross-make", "patches", "{n}-{v}".format_map(kwargs)))
            if os.path.exists(patch_dir):
                for it in sorted(os.listdir(patch_dir)):
                    try:
                        tools.patch(base_path="{n}-{v}".format_map(kwargs), patch_file=os.path.join(patch_dir, it))
                    except:
                        with tools.chdir("{n}-{v}".format_map(kwargs)):
                            os.system("patch -p1 -t < {}".format(os.path.join(patch_dir, it)))


class GCC(HelperDependency):
    name = "gcc"
    version = None
    _tar_ext = "tar.xz"
    _url = "https://ftp.gnu.org/pub/gnu/gcc/gcc-{v}/gcc-{v}.tar.xz"


class BinUtils(HelperDependency):
    name = "binutils"
    version = None
    _tar_ext = "tar.bz2"
    _url = "https://ftp.gnu.org/pub/gnu/binutils/binutils-{v}.tar.bz2"


class Musl(HelperDependency):
    name = "musl"
    _tar_ext = "tar.gz"
    _url = "https://www.musl-libc.org/releases/musl-{v}.tar.gz"


class Gmp(HelperDependency):
    name = "gmp"
    _tar_ext = "tar.bz2"
    _url = "https://ftp.gnu.org/pub/gnu/{n}/{n}-{v}.tar.bz2"


class Mpc(HelperDependency):
    name = "mpc"
    _tar_ext = "tar.gz"
    _url = "https://ftp.gnu.org/pub/gnu/mpc/mpc-{v}.tar.gz"


class Mpfr(HelperDependency):
    name = "mpfr"
    _tar_ext = "tar.bz2"
    _url = "https://ftp.gnu.org/pub/gnu/mpfr/mpfr-{v}.tar.bz2"


class Linux(HelperDependency):
    name = "linux"
    _tar_ext = "tar.xz"
    _url = "https://cdn.kernel.org/pub/linux/kernel/v4.x/linux-{v}.tar.xz"


class GCCMuslConan(ConanFile):
    name = "gcc_musl"
    version = "7.3.0"

    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of Gccmusl here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")
    
    settings = "os", "compiler", "build_type", "arch"
    options = {"target": ["x86_64-linux-musl", ],  # Build triple based on other options
               "gcc": ["6.4.0", ],
               "binutils": ["2.27", ],
               "musl": ["1.1.20", ],
               "gmp": ["6.1.1", ],
               "mpc": ["1.0.3", ],
               "mpfr": ["3.1.4", ],
               "linux": ["4.4.10", ]}
    default_options = {"target": "x86_64-linux-musl",
                       "gcc": "6.4.0",
                       "binutils": "2.27",
                       "musl": "1.1.20",
                       "gmp": "6.1.1",
                       "mpc": "1.0.3",
                       "mpfr": "3.1.4",
                       "linux": "4.4.10" }

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Linux required")

    def requirements(self):
        print(self.options.target)

    def source(self):
        if not os.path.exists("musl-cross-make"):
            self.run("git clone https://github.com/richfelker/musl-cross-make")

        gcc = GCC(version=self.options.gcc, output=self.output)
        gcc.source()

        binutils = BinUtils(version=self.options.binutils, output=self.output)
        binutils.source()

        musl = Musl(version=self.options.musl, output=self.output)
        musl.source()

        gmp = Gmp(version=self.options.gmp, output=self.output)
        gmp.source()

        mpc = Mpc(version=self.options.mpc, output=self.output)
        mpc.source()

        mpfr = Mpfr(version=self.options.mpfr, output=self.output)
        mpfr.source()

        linux = Linux(version=self.options.linux, output=self.output)
        linux.source()

        exit(0)

    def build(self):
        shutil.copyfile(os.path.join(self.source_folder, "musl-cross-make", "litecross", "Makefile"),
                        "Makefile")
        tools.save("config.mak", """
TARGET = {target}
HOST = 
MUSL_SRCDIR = {sf}/musl-1.1.20
GCC_SRCDIR = {sf}/gcc-6.4.0
BINUTILS_SRCDIR = {sf}/binutils-2.27
GMP_SRCDIR = {sf}/gmp-6.1.1
MPC_SRCDIR = {sf}/mpc-1.0.3
MPFR_SRCDIR = {sf}/mpfr-3.1.4
LINUX_SRCDIR = {sf}/linux-4.4.10
""".format(target=self.options.target, sf=self.source_folder))

        self.run("make all")


    def package(self):
        self.copy("*.h", dst="include", src="hello")
        self.copy("*hello.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["hello"]

