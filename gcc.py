from conans import tools, AutoToolsBuildEnvironment
from _base import BaseConanFile
import os


class GccConanFile(BaseConanFile):
	name = "gcc"
	version = "6.4.0"

	def requirements(self):
		self.requires("binutils/2.27@jgsogo/stable")

	def source(self):
		super(GccConanFile, self).source()
		url = "https://ftp.gnu.org/pub/gnu/gcc/gcc-{v}/gcc-{v}.tar.xz".format(v=self.version)
		tools.get(url, sha1=self._sha1(url))
		self._patch(self.name, self.version)

		gmp_url = "https://ftp.gnu.org/pub/gnu/gmp/gmp-6.1.1.tar.bz2"
		tools.get(gmp_url, sha1=self._sha1(gmp_url))
		self._patch("gmp", "6.1.1")
		os.symlink(os.path.join(self.source_folder, "gmp-6.1.1"), 
			os.path.join("{}-{}".format(self.name, self.version), 'gmp'))
		
		mpfr_url = "https://ftp.gnu.org/pub/gnu/mpfr/mpfr-3.1.4.tar.bz2"
		tools.get(mpfr_url, sha1=self._sha1(mpfr_url))
		self._patch("mpfr", "3.1.4")
		os.symlink(os.path.join(self.source_folder, "mpfr-3.1.4"), 
			os.path.join("{}-{}".format(self.name, self.version), 'mpfr'))
		
		mpc_url = "https://ftp.gnu.org/pub/gnu/mpc/mpc-1.0.3.tar.gz"
		tools.get(mpc_url, sha1=self._sha1(mpc_url))
		self._patch("mpc", "1.0.3")
		os.symlink(os.path.join(self.source_folder, "mpc-1.0.3"), 
			os.path.join("{}-{}".format(self.name, self.version), 'mpc'))
		

	def _prepare_sysroot(self):
		sysroot_path = os.path.join("{}-{}".format(self.name, self.version), 'sysroot')
		os.makedirs(sysroot_path)
		with tools.chdir(sysroot_path):
			os.makedirs('include')
			os.symlink('lib', 'lib32')
			os.symlink('lib', 'lib64')
			os.symlink('.', 'usr')
		return sysroot_path

	def build(self):
		binutils_bindir = os.path.join(self.deps_cpp_info['binutils'].rootpath, str(self.options.target), 'bin')
		sysroot_path = self._prepare_sysroot()

		with tools.chdir("{}-{}".format(self.name, self.version)):
			autotools = AutoToolsBuildEnvironment(self)
			"""
 --with-build-sysroot=/home/jgsogo/dev/musl-cross-make/build/local/x86_64-linux-musl/
	 obj_sysroot 
 AR_FOR_TARGET=/home/jgsogo/dev/musl-cross-make/build/local/x86_64-linux-musl/
 	obj_binutils/binutils/ar 
 AS_FOR_TARGET=/home/jgsogo/dev/musl-cross-make/build/local/x86_64-linux-musl/obj_binutils/gas/as-new 
 LD_FOR_TARGET=/home/jgsogo/dev/musl-cross-make/build/local/x86_64-linux-musl/obj_binutils/ld/ld-new 
 NM_FOR_TARGET=/home/jgsogo/dev/musl-cross-make/build/local/x86_64-linux-musl/obj_binutils/binutils/nm-new 
 OBJCOPY_FOR_TARGET=/home/jgsogo/dev/musl-cross-make/build/local/x86_64-linux-musl/obj_binutils/binutils/objcopy 
 OBJDUMP_FOR_TARGET=/home/jgsogo/dev/musl-cross-make/build/local/x86_64-linux-musl/obj_binutils/binutils/objdump 
 RANLIB_FOR_TARGET=/home/jgsogo/dev/musl-cross-make/build/local/x86_64-linux-musl/obj_binutils/binutils/ranlib 
 READELF_FOR_TARGET=/home/jgsogo/dev/musl-cross-make/build/local/x86_64-linux-musl/obj_binutils/binutils/readelf 
 STRIP_FOR_TARGET=/home/jgsogo/dev/musl-cross-make/build/local/x86_64-linux-musl/obj_binutils/binutils/strip-new
			"""
			args = ["--enable-languages=c,c++",
					"--disable-werror", 
					"--target={}".format(self.options.target),
					"--prefix=",
					"--libdir=/lib",
					"--disable-multilib",
					"--with-sysroot=/{}".format(self.options.target),
					"--enable-tls",
					"--disable-libmudflap",
					"--disable-libsanitizer",
					"--disable-gnu-indirect-function",
					"--disable-libmpx",
					"--enable-deterministic-archives",
					"--enable-libstdcxx-time",
					"--with-build-sysroot={}".format(sysroot_path),
					"AR_FOR_TARGET={}".format(os.path.join(binutils_bindir, "ar")),
					"AS_FOR_TARGET={}".format(os.path.join(binutils_bindir, "as")),
					"LD_FOR_TARGET={}".format(os.path.join(binutils_bindir, "ld")),
					"NM_FOR_TARGET={}".format(os.path.join(binutils_bindir, "nm")),
					"OBJCOPY_FOR_TARGET={}".format(os.path.join(binutils_bindir, "objcopy")),
					"OBJDUMP_FOR_TARGET={}".format(os.path.join(binutils_bindir, "objdump")),
					"RANLIB_FOR_TARGET={}".format(os.path.join(binutils_bindir, "ranlib")),
					"READELF_FOR_TARGET={}".format(os.path.join(binutils_bindir, "readelf")),
					"STRIP_FOR_TARGET={}".format(os.path.join(binutils_bindir, "strip")),
					]
			autotools.configure(args=args)
			"make MULTILIB_OSDIRNAMES= INFO_DEPS= infodir= ac_cv_prog_lex_root=lex.yy.c MAKEINFO=false"
			args = ["MULTILIB_OSDIRNAMES=",
					"INFO_DEPS=",
					"infodir=",
					"ac_cv_prog_lex_root=lex.yy.c",
					"MAKEINFO=false"]
			make_args = args + ["MAKE=make {}".format(" ".join(args)),]
			autotools.make(args=make_args)

	def package(self):
		with tools.chdir("{}-{}".format(self.name, self.version)):
			autotools = AutoToolsBuildEnvironment(self)
			autotools.install()
