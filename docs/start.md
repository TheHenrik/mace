# Getting started

Fork the [template repository](https://github.com/TheHenrik/mace-template) and clone it to your computer. Set up a python environment of your choice. It is recommended to use [uv](https://docs.astral.sh/uv/). This guide will assume you did, but other ways will still work.

As soon as you haave cloned the repository, set up your python with:
```sh
uv init
uv python install
```

To specify a version use

```sh
uv python install 3.13
```

Than build your dependencies with

```sh
uv add pymace 
```

Create the file ./python/vehicle.py and ./python/mission.py
```py
def vehicle():
    pass
```

```py
from vehicle import vehicle

def main():
    airplane = vehicle()
    airplane.mission_execute()

    print(airplane.results())
    
if __name__ == "__main__":
    main()
```