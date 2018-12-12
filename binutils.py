from conans import tools, AutoToolsBuildEnvironment
from _base import BaseConanFile


class BinutilsConanFile(BaseConanFile):
	name = "binutils"
	version = "2.27"

	def source(self):
		super(BinutilsConanFile, self).source()
		url = "https://ftp.gnu.org/pub/gnu/binutils/binutils-{}.tar.bz2".format(self.version)
		tools.get(url, sha1=self._sha1(url))
		self._patch(self.name, self.version)

	def build(self):
		with tools.chdir("{}-{}".format(self.name, self.version)):
			autotools = AutoToolsBuildEnvironment(self)
			"--disable-werror --target=x86_64-linux-musl --prefix= --libdir=/lib --disable-multilib --with-sysroot=/x86_64-linux-musl"
			args = ["--disable-werror", 
					"--target={}".format(self.options.target),
					"--disable-multilib",
					"--with-sysroot=/{}".format(self.options.target),
					"--libdir=/lib",
					#"--prefix=",
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
			args = ["MULTILIB_OSDIRNAMES=",
					"INFO_DEPS=",
					"infodir=",
					"ac_cv_prog_lex_root=lex.yy.c",
					"MAKEINFO=false"]
			make_args = args + ["MAKE=make {}".format(" ".join(args)),
								#"DESTDIR={}".format(self.package_folder),
								]
			autotools.install(args=make_args)
