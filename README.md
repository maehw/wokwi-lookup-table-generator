# wokwi lookup table generator

Generator for wokwi schematics that implement lookup tables in conjunctive normal form (CNF), i.e. with AND and OR gates.

This project is written in Python3.

This project is WIP. Feel free to contribute, open issues, etc.


## Installation and dependencies

TODO: Move dependencies into `requirements.txt` and resolve them.

> qm is inside /usr/local/lib/python3.10/site-packages/quine_mccluskey
> `pip3 install quine-mccluskey` installs it, but is cannot be found; why?


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

The unused input pin of a 2 input AND gate can
1. either be pulled HIGH or
1. be connected to the other input
The unused input pin of a 2 input OR gate can
1. either be pulled LOW or
1. be connected to the other input

In the past I had used the first approach which takes more effort (adding a GND and a VCC block and adding connections to it).
I've switch to the second approach as this can be realized by adding a short wire connection from one inport to the other - and it's generic for AND and OR gates.
