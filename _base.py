import os
import shutil
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class BaseConanFile(ConanFile):
    name = None
    version = None

    settings = "os", "compiler", "build_type", "arch"
    options = {"target": ["x86_64-linux-musl", ], }  # Build triple based on other options
    default_options = {"target": "x86_64-linux-musl", }

    exports = "_base.py"

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Linux required")

    def source(self):
        self.run("git clone https://github.com/richfelker/musl-cross-make")

    def _sha1(self, url):
        basename = os.path.basename(url)
        sha1_path = os.path.join(self.source_folder, "musl-cross-make", "hashes", "{}.sha1".format(basename))
        if os.path.exists(sha1_path):
            return tools.load(sha1_path).split(" ", 1)[0]
        return None

    def _patch(self, name, version):
        basename = "{}-{}".format(name, version)

        patch_dir = os.path.abspath(os.path.join(self.source_folder, "musl-cross-make", "patches", basename))
        if os.path.exists(patch_dir):
            self.output.info("Apply patches to {}".format(basename))
            for it in sorted(os.listdir(patch_dir)):
                try:
                    tools.patch(base_path=basename, patch_file=os.path.join(patch_dir, it))
                except:
                    with tools.chdir(basename):
                        os.system("patch -p1 -t < {}".format(os.path.join(patch_dir, it)))
        else:
            self.output.warn("Patches not found for {}".format(basename))
