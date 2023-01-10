# Conan Recipe for the Gurobi LP/QP/MIP solver

The repository provides a recipe to package the [Gurobi solver](https://www.gurobi.com/) using [Conan](https://conan.io/).

## Usage

Within the repository root folder, run the following command (whereby `VERSION` specifies the Gurobi version that should be packaged):

```shell
$ VERSION="10.0.0" conan create .
```

## Supported Compilers and Operating Systems

As Gurobi comes with [limited support for compilers](https://www.gurobi.com/solutions/gurobi-optimizer/supported-platforms/),
this packages uses only the C-library provided by Gurobi but compiles the C++-library from the sources.

At the moment, this recipe is tested on Linux and MacOS using GCC, Clang and Apple-Clang.

## Maintainer

This project is maintained by Ivo Hedtke `ivo (dot) hedtke (at) dbschenker (dot) com`.

## Code of Conduct

see [code_of_conduct.md](code_of_conduct.md)

## Contributor License Agreement

This project does not use a CLA.

## License

Gurobi itself has a proprietary license.
This recipe is licensed under the Apache-2 license.
