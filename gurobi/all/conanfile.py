from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import collect_libs, copy, download, get, rmdir, rm


class Gurobi(ConanFile):
    name = "gurobi"
    settings = "os", "arch", "compiler", "build_type"
    description = "Gurobi solver for LP/QP/MIP problems"
    homepage = "https://www.gurobi.com/"
    license = None
    topics = ("linear", "programming", "simplex", "solver")
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

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
        build_folder = "buildfolder"
        if self.settings.os == "Linux":
            get(self, **self.conan_data["sources"][self.version][str(self.settings.os)], destination=build_folder)
            content_dir = f"{build_folder}/{version_no_dots}/linux64"
        else:
            download(self, **self.conan_data["sources"][self.version][str(self.settings.os)], filename="grb")
            self.run(f"pkgutil --expand-full grb {build_folder}")
            rm(self, "grb", ".")
            content_dir = f"{build_folder}/gurobi{self.version}_macos_universal2.component.pkg/Payload/Library/{version_no_dots}/macos_universal2"
        copy(self, pattern="*", src=f"{content_dir}/src/cpp", dst="src")
        copy(self, pattern=self._get_shared_lib_name(), src=f"{content_dir}/lib", dst="lib")
        copy(self, pattern="gurobi*.h", src=f"{content_dir}/include", dst="include")
        rmdir(self, build_folder)

    def export_sources(self):
        self.copy("CMakeLists.txt")

    def generate(self):
        # we build only the C++ lib and copy the C lib
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        # header
        self.copy(pattern="include/gurobi*.h", dst="include", keep_path=False)
        # C++ lib
        self.copy(pattern="libgurobi_c++.a", dst="lib", keep_path=False)
        # C lib
        self.copy(pattern=f"lib/{self._get_shared_lib_name()}", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "m", "pthread", "rt"])
