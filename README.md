# wokwi lookup table generator

Generator for wokwi schematics that implement lookup tables in conjunctive normal form (CNF), i.e. with AND and OR gates.

This project is written in Python3.

This project is WIP. Feel free to contribute, open issues, etc.


## Usage

```
$ python3 generate.py -h
usage: generate.py [-h] [-v] [-f IN_FILE] [-o OUT_FILE]

generate.py is a lookup table generator tool for wokwi

options:
  -h, --help            show this help message and exit
  -v, --verbose         log level (-v: INFO, -vv: DEBUG) (default: 0)
  -f IN_FILE, --file IN_FILE
                        path to JSON logic input file; if none is given, stdout is used (default: logic.json)
  -o OUT_FILE, --outfile OUT_FILE
                        path to generated wokwi schematic file (default: None)
```

Examples:

Only specifying the input file name, will dump the wokwi schematic via `stdout`:

```
python3 generate.py -f 2bit_half_adder.logic.json
```

Only specifying the input file name, will dump the wokwi schematic via `stdout` (piped to `/dev/null`), log level `DEBUG`:

```
python3 generate.py -f 2bit_half_adder.logic.json -vv > /dev/null
```

Specify an output file for the wokwi schematic:

```
python3 generate.py -f 2bit_half_adder.logic.json -o 2bit_half_adder.diagram.json
```

Specify an output file for the wokwi schematic externally but also show contents on `stdout` by [piping it through `tee`](https://en.wikipedia.org/wiki/Tee_(command)):

```
python3 generate.py -f 2bit_half_adder.logic.json | tee 2bit_half_adder.diagram.json
```


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
- use a more object-oriented approach for everything
- implement interactive mode
- perform sanity checks to see if all parts are connected,
  some may be unused due to bugs (probably rounding)


## Demo designs

* `2bit_half_adder.logic.json`: 2-bit half adder (is not fully working yet)
* `2bit_full_adder.logic.json`: 2-bit full adder (is not fully working yet)
* `limited-ascii_7segment_lut.logic.json`: limited ASCII character range to 7-segment Wokwi display (is not fully working yet?)
* `4bit-popcount.json`: 4-bit popcount (makes the generator hang up)

For descriptions of the demo designs, inspect their JSON files.

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
