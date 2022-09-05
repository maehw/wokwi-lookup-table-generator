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


After having generated your diagram JSON file, ...

1. go to [wokwi.com](https://wokwi.com)
1. start a new project
   (e.g. choosing "Arduino Nano", that's not really relevant for the logic designs unless you want to control/test them with an Arduino or other microcontroller; however, all components will be deleted in the next steps)
1. switch the editor view from tab `sketch.ino` to tab `diagram.json`
1. select all the text in the editor and delete it
1. paste the contents of the generated JSON files
1. add components on the input and output side of your design
1. have fun simulating everything

> **Warning**
> When using an 8-pin DIP switch for the inputs, make sure to connect one end to VCC and the other end to a pull-down resistor (connected to GND). Otherwise the output may act in a non-deterministic way.

> **Note**
> - You currently need to optimize the wires of your layout manually.
> - You can add textual descriptions to your schematic using parts of type `wokwi-text`.


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

For descriptions of the demo designs, inspect their JSON files.

> **Warning**
> The Quine McCluskey algorithm currently does not give deterministic results. An issue has been opened [here](https://github.com/tpircher/quine-mccluskey/issues/8).

Some demos are working, some seem to cause trouble.

### Working demos

* [2bit_half_adder.logic.json]: 2-bit half adder

  ([Wokwi demo project](https://wokwi.com/projects/341979369318646355))

* [2bit_full_adder.logic.json]: 2-bit full adder

  ([Wokwi demo project](https://wokwi.com/projects/341985679348073043))
* [2bit_and.logic.json]: 2-bit AND (as simple as an AND gate, but generated using a truth table)

  ([Wokwi demo project](https://wokwi.com/projects/341992203508253267))

* [2bit_or.logic.json]: 2-bit OR (as simple as an OR gate, but generated using a truth table)

  ([Wokwi demo project](https://wokwi.com/projects/341992743611925075))


### Non-working demos

* [limited-ascii_7segment_lut.logic.json]: limited ASCII character range to 7-segment Wokwi display

  ([basic Wokwi demo project](https://wokwi.com/projects/341987347359859282), [advanced Wokwi demo project](https://wokwi.com/projects/341989925253546578) cycling through the character set with an Arduino disclosing encoding errors)

* [4bit-popcount.json]: 4-bit popcount (makes the generator hang up)


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
