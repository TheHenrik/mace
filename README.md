# Model aircraft calculation and evaluation

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Tests](https://github.com/TheHenrik/mace/actions/workflows/tests.yaml/badge.svg)

MACE is a tool written by the Akamodell Stuttgart for evaluating and calculating self build and designed model aircraft for private use and competitions like [ACC](https://en.wikipedia.org/wiki/Air_Cargo_Challenge).

## How to install

If you want to install this project, run:

```powershell
pip install "git+https://github.com/TheHenrik/mace.git"
```

or if you want to edit the package, clone the repository and run:

```powershell
pip install -e .
```

 But consider installing all optional dependencies:

 ```powershell
 pip install -e .[dev]
 ```

To open the mace-gui run:

```powershell
mace-gui
```

If you want to uninstall, run:

```powershell
pip uninstall mace
```

## Documentation

To be included, as well as docstrings.

## Creator

This package is created for the [Akamodell Stuttgart](http://www.akamodell.de/) by [Tjalf Stadel](https://github.com/TheHenrik) and Gregor Zwickl as our Bachelor Thesis and is supervised by the [IFB](https://www.ifb.uni-stuttgart.de/).
