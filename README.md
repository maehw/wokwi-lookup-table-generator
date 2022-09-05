# wokwi lookup table generator

Generator for wokwi schematics that implement lookup tables in conjunctive normal form (CNF), i.e. with AND and OR gates.

This project is written in Python3.

This project is WIP. Feel free to contribute, open issues, etc.


## Installation and dependencies

Resolve all requirements using `pip3`:

```
pip3 install -r requirements.txt
```

This project depends on the package `quine-mccluskey` a [Python implementation of the Quine McCluskey algorithm](https://pypi.org/project/quine-mccluskey/).

The author says:

> This implementation of the Quine McCluskey algorithm has no inherent limits (other than the calculation time) on the size of the inputs.

> **Warning**
> The Quine McCluskey algorithm currently does not give deterministic results. An issue has been opened [here](https://github.com/tpircher/quine-mccluskey/issues/8).


## TODOs

- document limitations
- add assertions
- make log level configurable
- use a more object-oriented approach for everything
- implement interactive mode
- allow configuration data to be fed in as an external file
- perform sanity checks to see if all parts are connected,
  some may be unused due to bugs (probably rounding)


## Termination of unsed gate inputs

I have basically identified two termination strategies:

The unused input pin of a 2 input *AND* gate can

1. either be pulled HIGH or
1. be connected to the other input

The unused input pin of a 2 input *OR* gate can

1. either be pulled LOW or
1. be connected to the other input

In the past I had used the first approach which takes more effort (adding a GND and a VCC block and adding connections to it).
I've switch to the second approach as this can be realized by adding a short wire connection from one inport to the other - and it's generic for AND and OR gates.
