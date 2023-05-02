from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import collect_libs, copy, download, get, rmdir, rm, rename
from conan.tools.apple import fix_apple_shared_install_name
from os.path import join


class Gurobi(ConanFile):
    name = "gurobi"
    settings = "os", "arch", "compiler", "build_type"
    description = "Gurobi solver for LP/QP/MIP problems"
    homepage = "https://www.gurobi.com/"
    license = None
    topics = ("linear", "programming", "simplex", "solver")
    options = {
        "fPIC": [True, False],
        "shared": [True]  # required to call fix_apple_shared_install_name later
    }
    default_options = {"fPIC": True, "shared": True}
    package_type = "library"

    def _get_shared_lib_name(self):
        major_version_no_dots = ''.join(self.version.split('.')[:-1])
        extension = "so" if self.settings.os == "Linux" else "dylib"
        return f"libgurobi{major_version_no_dots}.{extension}"

    def validate(self):
        if self.settings.os not in ["Linux", "Macos"]:
            raise ConanInvalidConfiguration(f"OS {self.settings.os} not supported")
        if self.settings.compiler not in ["gcc", "clang", "apple-clang"]:
            raise ConanInvalidConfiguration(f"Compiler {self.settings.compiler} not supported")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def generate(self):
        # we build only the C++ lib and copy the C lib
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        # equivalent of source(), but there it is not allowed to depend on settings, thus we do it here, see
        # https://docs.conan.io/2/reference/conanfile/methods/source.html
        version_no_dots = "gurobi" + self.version.replace('.', '')
        build_folder = "buildfolder"
        if self.settings.os == "Linux":
            get(self, **self.conan_data["sources"][self.version][str(self.settings.os)], destination=build_folder)
            content_dir = f"{build_folder}/{version_no_dots}/linux64"
            rm(self, pattern=self._get_shared_lib_name(), folder=f"{content_dir}/lib")
            rename(self, src=f"{content_dir}/lib/libgurobi.so.{self.version}",
                   dst=f"{content_dir}/lib/{self._get_shared_lib_name()}")
        else:
            download(self, **self.conan_data["sources"][self.version][str(self.settings.os)], filename="grb")
            self.run(f"pkgutil --expand-full grb {build_folder}")
            rm(self, "grb", ".")
            content_dir = f"{build_folder}/gurobi{self.version}_macos_universal2.component.pkg/Payload/Library/{version_no_dots}/macos_universal2"
        copy(self, pattern="*", src=f"{content_dir}/src/cpp", dst="src")
        copy(self, pattern=self._get_shared_lib_name(), src=f"{content_dir}/lib", dst="lib")
        copy(self, pattern="gurobi*.h", src=f"{content_dir}/include", dst="include")
        rmdir(self, build_folder)
        # real build
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        # header
        copy(self, pattern="*.h", src=join(self.build_folder, "include"), dst=join(self.package_folder, "include"))
        # C++ lib
        copy(self, "libgurobi_c++.a", src=self.build_folder, dst=join(self.package_folder, "lib"))
        # C lib
        copy(self, self._get_shared_lib_name(), src=join(self.build_folder, "lib"), dst=join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)  # pre-built C lib contains an absolute path

    def package_info(self):
        self.cpp_info.libsdirs = ["lib"]
        self.cpp_info.libs = [self._get_shared_lib_name(), "gurobi_c++"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "m", "pthread", "rt"])
