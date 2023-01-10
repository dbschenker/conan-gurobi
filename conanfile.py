from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools import files
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import download, get
import os


class Gurobi(ConanFile):
    name = "gurobi"
    settings = "os", "arch", "compiler", "build_type"
    version = os.getenv("VERSION")
    description = "Gurobi solver for LP/QP/MIP problems"
    homepage = "https://www.gurobi.com/"
    license = None
    topics = ("linear", "programming", "simplex", "solver")
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    _root_dir = None

    def _package_url(self) -> str:
        ver = '.'.join(self.version.split('.')[:-1])
        filename = f"gurobi{self.version}_" + ("linux64.tar.gz" if self.settings.os == "Linux" else "macos_universal2.pkg")
        return f"https://packages.gurobi.com/{ver}/{filename}"

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

    def source(self):
        version_no_dots = "gurobi" + self.version.replace('.', '')
        build_folder = "build"
        if self.settings.os == "Linux":
            get(self, self._package_url(), destination=build_folder)
            self._root_dir = f"{build_folder}/{version_no_dots}/linux64"
        else:
            download(self, self._package_url(), filename="grb")
            self.run(f"pkgutil --expand-full grb {build_folder}")
            self._root_dir = f"{build_folder}/gurobi{self.version}_macos_universal2.component.pkg/Payload/Library/{version_no_dots}/macos_universal2"
        files.copy(self, pattern="*", src=f"{self._root_dir}/src/cpp", dst=self.export_sources_folder, keep_path=False)
        files.copy(self, pattern="gurobi*.h", src=f"{self._root_dir}/include", dst=self.export_sources_folder, keep_path=False)

    def export_sources(self):
        self.copy("CMakeLists.txt")

    def build(self):
        # we build only the C++ lib and copy the C lib
        tc = CMakeToolchain(self)
        tc.generate()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        # header
        self.copy(pattern=f"{self._root_dir}/include/gurobi*.h", dst="include", keep_path=False)
        # C++ lib
        self.copy(pattern="libgurobi_c++.a", dst="lib", keep_path=False)
        # C lib
        self.copy(pattern=f"{self._root_dir}/lib/{self._get_shared_lib_name()}", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["libgurobi_c++.a", self._get_shared_lib_name()]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "m", "pthread", "rt"]
