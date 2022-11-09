# Wokwi lookup table (LUT) generator

## What is this all about?

This git repository contains a **generator for [wokwi](https://wokwi.com) schematics that implement lookup tables** (defined by a truth table and some more meta data in a JSON file, see the [./demos](demos) subdirectory.

But what is wokwi? Wokwi is a free, browser-based simulator that supports different Arduino and several other boards and components (such as LEDs, buttons, switches, sensors, ...). It also has been used during [#TinyTapeout](https://tinytapeout.com) in August/September 2022 - an educational project that "aims to make it easier and cheaper than ever to get your digital designs manufactured on a real chip". So oversimplified you can also easily simulate and generate ASIC designs - from a very simple boolean algebra design description (truth tables).

How does this work internally? See a separate section below the "Usage" section

Language: This project is written in Python3.

> **Note**
> This project is work in progress. It is known that not all designs are generated correctly, so there are still some bugs.


## Contribution

Feel free to contribute, open issues, [work on existing issues](https://github.com/maehw/wokwi-lookup-table-generator/issues), etc.
To contribute to the project, fork this GitHub repository and create a pull request. Detailed instructions can be found at https://docs.github.com/en/get-started/quickstart/contributing-to-projects. I'll be happy to review the code diff and eventually merge it into the original repo here.


## Usage

```
usage: generate.py [-h] [-v] [-f IN_FILE] [-o OUT_FILE] [-p] [-c] [-t] [-tt]

generate.py is a lookup table generator tool for wokwi

options:
  -h, --help            show this help message and exit
  -v, --verbose         log level (-v: INFO, -vv: DEBUG) (default: 0)
  -f IN_FILE, --file IN_FILE
                        path to JSON logic input file; if none is given, stdout is used (default: logic.json)
  -o OUT_FILE, --outfile OUT_FILE
                        path to generated wokwi schematic file (default: None)
  -p, --parts_only      dump wokwi parts list only (default: False)
  -c, --connections_only
                        dump wokwi connections list only (default: False)
  -t, --test            add an Arduino MEGA as test framework and generate Arduino verification code (default: False)
  -tt, --tinytapeout    add default parts used in tinytapeout wokwi template schematic (default: False)
```

Examples:

Only specifying the input file name, will dump the wokwi schematic via `stdout`:

```
python3 generate.py -f ./demos/2bit_half_adder.logic.json
```

Only specifying the input file name, will dump the wokwi schematic via `stdout` (piped to `/dev/null`), log level `DEBUG`:

```
python3 generate.py -f ./demos/2bit_half_adder.logic.json -vv > /dev/null
```

Specify an output file for the wokwi schematic:

```
python3 generate.py -f ./demos/2bit_half_adder.logic.json -o 2bit_half_adder.diagram.json
```

Specify an output file for the wokwi schematic externally but also show contents on `stdout` by [piping it through `tee`](https://en.wikipedia.org/wiki/Tee_(command)):

```
python3 generate.py -f ./demos/2bit_half_adder.logic.json | tee 2bit_half_adder.diagram.json
```

Switches `-p` and `-c` allow to limit the dump to wokwi parts ony respectively wokwi connections only.

This feature can be used to modify existing designs only. The following command can be used on Mac OS X to **copy** the parts of the design into the **p**aste **b**uffer:

```
python3 generate.py -f ./demos/bcd_7segment_lut.logic.json -p | sed 's/[{}]//' | pbcopy
```

Specify an output file for the wokwi schematic; also generate an Arduino sketch for automated verification and add and connect an Arduino MEGA in the wokwi schematic:

```
python3 generate.py -f ./demos/2bit_half_adder.logic.json -o 2bit_half_adder.diagram.json -t
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


## Demo designs

For descriptions of the demo designs, inspect their JSON files in the `./demos` subdirectory of this repo.

> **Warning**
> The Quine McCluskey algorithm currently does not give deterministic results. An issue has been opened [here](https://github.com/tpircher/quine-mccluskey/issues/8).

Some demos are working, some seem to cause trouble.

### Working demos

* [`2bit_half_adder.logic.json`](./demos/2bit_half_adder.logic.json): 2-bit half adder; ([Wokwi demo project](https://wokwi.com/projects/341979369318646355))

* [`2bit_full_adder.logic.json`](./demos/2bit_full_adder.logic.json): 2-bit full adder; ([Wokwi demo project](https://wokwi.com/projects/341985679348073043))

* [`2bit_and.logic.json`](./demos/2bit_and.logic.json): 2-bit AND ([Wokwi demo project](https://wokwi.com/projects/341992203508253267)); (as simple as an AND gate, but generated using a truth table)

* [`2bit_or.logic.json`](./demos/2bit_or.logic.json): 2-bit OR ([Wokwi demo project](https://wokwi.com/projects/341992743611925075)); (as simple as an OR gate, but generated using a truth table)

* [`limited-ascii_7segment_lut.logic.json`](./demos/limited-ascii_7segment_lut.logic.json): limited ASCII character range to 7-segment Wokwi display; ([basic Wokwi demo project](https://wokwi.com/projects/341987347359859282), [advanced Wokwi demo project](https://wokwi.com/projects/342600282267451988) cycling through the character set with an Arduino and showing the outputs on a common cathose 7-segment display)


### Non-working demos

* [`4bit-popcount.json`](./demos/4bit-popcount.json): 4-bit popcount (makes the generator hang up)


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


## How does this work internally?

The generator is fed with a truth table describing the boolean algebra to be implemented.

The generator implements the lookup tables (truth tables) in conjunctive normal form (CNF)**, i.e. with AND and OR gates.

Let's have a look at the example of a 2-bit half adder: "Logic that adds two numbers and produces a sum bit (S) and carry bit (C)."

The truth table looks as follows (`a` and `b` are inputs, `S` (sum) and `C` (carry) are outputs):

| a | b | S | C |
|---|---|---|---|
| 0 | 0 | 0 | 0 |
| 0 | 1 | 1 | 0 |
| 1 | 0 | 1 | 0 |
| 1 | 1 | 0 | 1 |

This can also be written as equations with functions of boolean algebra (using so called minterms):

```
S = ~a*b + a*~b
C = a*b
```

where

* `~` represents inversion (a `NOT` gate),
* `*` represents a logical `AND`(an `AND` gate),
* `+` represents a logical `OR` an `OR` gate).

That also explains the term "sum of products" (SOP).


For better readability the `*` are often omitted, leaving us with:

```
S = ~ab + a~b
C = ab
```

The conversion from truth table to boolean algebra is done with a [Python implementation of the Quine McCluskey algorithm](https://pypi.org/project/quine-mccluskey/). Please note that these optimizations are not really required as the ASIC toolchain will take care of optimization (and know the kind of hardware cells being available on the target hardware), but it helps to understand own digital designs and their implementation.

The algorithm basically performs the following steps (be careful as this concept image does not match the previously used example):

![concept](https://user-images.githubusercontent.com/6305922/189659328-9eaca4a9-6210-4447-bb89-966fe479e801.png)

* Insert buffers for the inputs and `NOT` gates for the inverted inputs (green step)
* Insert `AND` gates and connect pairs of inputs to those `AND` gates (make products of two multiplicands; first yellow step)
* Insert more `AND` gates and connect them so that a single product ends with one final `AND` gate to get a summand for the additional stage (second yellow step)
* Insert `OR` gates and connect pairs of inputs to those `OR` gates (make sums of two summands; first blue step)
* Insert more `OR` gates and connect them so that a single sum ends with one final `OR` gate to get the final output for the boolean algebraic function


Further read: [Département d'informatique et de recherche opérationnelle - Université de Montréal: LOGIC SYNTHESIS AND TWO LEVEL LOGIC OPTIMIZATION](http://www.iro.umontreal.ca/~dift6221/demicheli4/twolevel1.4.ps.pdf)


## Tiny Tapeout

See also:

* https://tinytapeout.com/
* [Tiny Tapeout 2 Guide](https://github.com/maehw/wokwi-lookup-table-generator/wiki/Tiny-Tapeout-2--Guide#generating-and-verifying-wokwi-designs-with-combinational-logic) - Generating and verifying wokwi designs with combinational logic


## TODOs

- document limitations
- add assertions
- use a more object-oriented approach for everything
- implement interactive mode
- perform sanity checks to see if all parts are connected,
  some may be unused due to bugs (probably rounding)

Some TODOs or ideas are already visible in the [issues tab](https://github.com/maehw/wokwi-lookup-table-generator/issues). Especially have a look at the issues labeled `good first issue` and `help wanted`.
