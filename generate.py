#!/usr/bin/env python3
import json
import math
import coloredlogs, logging
from os import linesep
from quine_mccluskey import qm
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, BooleanOptionalAction

# Copyright (c) maehw, 2022
# wokwi-lookup-table-generator is licensed under the GNU General Public License v3.0
# Copyright and license notices must be preserved. Contributors provide an express grant of patent rights.

if __name__ == '__main__':
    parser = ArgumentParser(description='%(prog)s is a lookup table generator tool for wokwi',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('-v', '--verbose',
                        action='count',
                        help='log level (-v: INFO, -vv: DEBUG)',
                        default=0)

    parser.add_argument('-f', '--file',
                        dest='in_file',
                        help='path to JSON logic input file; if none is given, stdout is used',
                        default="logic.json")

    parser.add_argument('-o', '--outfile',
                        dest='out_file',
                        help='path to generated wokwi schematic file',
                        default=None)

    parser.add_argument('-p', '--parts_only',
                       action=BooleanOptionalAction,
                       help='dump wokwi parts list only',
                       default=0)

    parser.add_argument('-c', '--connections_only',
                        action=BooleanOptionalAction,
                        help='dump wokwi connections list only',
                        default=0)

    parser.add_argument('-t', '--test',
                       action=BooleanOptionalAction,
                       help='add an Arduino MEGA as test framework and generate Arduino verification code',
                       default=0)

    parser.add_argument('-tt', '--tinytapeout',
                       action=BooleanOptionalAction,
                       help='add default parts used in tinytapeout wokwi template schematic',
                       default=0)

    args = parser.parse_args()

    # Create and configure logger object
    log = logging.getLogger(__name__)
    #coloredlogs.install(level='DEBUG', fmt='%(asctime)s [%(levelname)8s] %(message)s')

    if args.verbose > 0:
        log_level='INFO'
        if args.verbose > 1:
            log_level='DEBUG'
    else:
        log_level='WARNING'

    coloredlogs.install(level=log_level, fmt='[%(levelname)8s] %(message)s')

    out_filename = 'diagram.json'

    # templates for wokwi part instances
    global wokwi_design
    wokwi_design = {
      "version": 1,
      "author": "maehw",
      "editor": "wokwi",
      "parts": [],
      "connections": []
    }

    wokwi_gate_not = {
        "type": "wokwi-gate-not",
        "id": None,
        "top": 0,
        "left": 0,
        "attrs": {}
    }

    wokwi_gate_buffer = {
        "type": "wokwi-gate-buffer",
        "id": None,
        "top": 0,
        "left": 0,
        "attrs": {}
    }

    wokwi_gate_and2 = {
        "type": "wokwi-gate-and-2",
        "id": None,
        "top": 0,
        "left": 0,
        "attrs": {}
    }

    wokwi_gate_or2 = {
        "type": "wokwi-gate-or-2",
        "id": None,
        "top": 0,
        "left": 0,
        "attrs": {}
    }

    wokwi_arduino_mega = {
        "type": "wokwi-arduino-mega",
        "id": "mega",
        "top": -400,
        "left": -500,
        "rotate": 90,
        "attrs": {}
    }

    wokwi_dip_switch8 = {
        "type": "wokwi-dip-switch-8",
        "id": "sw1",
        "top": -188,
        "left": -400,
        "rotate": 90,
        "attrs": {}
    }

    wokwi_clock_generator = {
        "type": "wokwi-clock-generator",
        "id": "clock1",
        "top": -300,
        "left": -400,
        "attrs": {}
    }

    wokwi_chip_input_8pins = {
        "type": "chip-input-8-pins",
        "id": "chip1",
        "top": -200,
        "left": -230,
        "attrs": { "verilogRole": "input" }
    }

    wokwi_chip_output_8pins = {
        "type": "chip-output-8-pins",
        "id": "chip2",
        "top": -200,
        "left": 900,
        "attrs": { "verilogRole": "output" }
    }

    wokwi_7segment = {
        "type": "wokwi-7segment",
        "id": "sevseg1",
        "top": -200,
        "left": 1100,
        "attrs": { "common": "cathode" }
    }

    wokwi_slide_switch = {
        "type": "wokwi-slide-switch",
        "id": "sw2",
        "top": -320,
        "left": -300,
        "attrs": { "value": "1" }
    }

    wokwi_pushbutton = {
        "type": "wokwi-pushbutton",
        "id": "btn1",
        "top": -410,
        "left": -400,
        "attrs": { "color": "grey", "label": "Step", "bounce": "0" }
    }

    wokwi_vcc = {
        "type": "wokwi-vcc",
        "id": None,
        "top": 0,
        "left": 0,
        "attrs": {}
    }

    wokwi_gnd = {
        "type": "wokwi-gnd",
        "id": None,
        "top": 0,
        "left": 0,
        "attrs": {}
    }

    # ------------------------------------------------------------------------------
    # user specific output style and laoyut definition

    wokwi_gate_spacing_v = 60
    wokwi_gate_spacing_h = 120

    sym_negation = '~' # could also be 'NOT '
    sym_and = '' # could also be ' AND ' / '*'
    sym_or = ' + ' # could also be ' OR '
    sym_term_start = '' # '('
    sym_term_end = '' # ')'

    # default connection instructions:
    # global default and special default for termination connections
    default_con_instr = ["h10", "*", "h-10"]
    default_con_termination_instr = ["h-20", "*", "h-20"]

    # colors for connections from X-type to Y-type (read from left to right, same as the signal flow)
    con_color_neginput_and = "blue"
    con_color_input_and = "brown"
    con_color_and_and_interconnect = "orange"
    con_color_and_or_interconnect = "purple"
    con_color_or_or_interconnect = "green"
    con_color_or_output = "cyan"
    con_color_termination = "black"
    con_color_arduino_interconnect = "black"
    con_color_vcc_interconnect = "red"
    con_color_gnd_interconnect = "black"
    con_color_7seg_interconnect = "green"
    con_color_board_interconnect = "green"

    arduino_sketch_template_file = "sketch.ino.template"

    global global_and_gate_idx
    global_and_gate_idx = -1
    global global_and_gate_used_inports
    global_and_gate_used_inports = 0

    global global_or_gate_idx
    global_or_gate_idx = -1
    global global_or_gate_used_inports
    global_or_gate_used_inports = 0

    # ------------------------------------------------------------------------------
    # helper functions

    def calc_num_and_gates(num_all_inputs):
        num_gates = 0
        num_stages = 0
        if num_all_inputs < 2:
            num_gates = 1
            num_stages = 1
            # strategy: always use at least one AND gate (not only a straight wire)!
        else:
            stage_inputs = num_all_inputs
            done = False
            while(not done):
                num_stages = num_stages + 1
                num_gates_stage = math.ceil(stage_inputs/2)
                #print(f"Number of gates in stage #{num_stages}: {num_gates_stage}")

                num_gates = num_gates + num_gates_stage
                stage_inputs = num_gates_stage

                if num_gates_stage == 1:
                    done = True
        return (num_gates, num_stages)

    def get_part_by_id(id):
        part = next((item for item in wokwi_design["parts"] if item['id'] == id), None)
        return part

    def delete_part_by_id(id):
        wokwi_design["parts"] = [d for d in wokwi_design["parts"] if d.get('id') != id]

    def terminate_current_and_gate():
        global global_and_gate_idx
        global global_and_gate_used_inports

        if global_and_gate_idx >= 0:
            num_open_ports = 2 - global_and_gate_used_inports
            if num_open_ports > 0:
                log.debug(f"    Terminating AND gate #{global_and_gate_idx}'s {num_open_ports} open input(s)")
                con = [ f"gate_and_{global_and_gate_idx}:A", f"gate_and_{global_and_gate_idx}:B",
                        con_color_termination, default_con_termination_instr ]
                wokwi_design["connections"].append(con)
                log.debug("      Connection: "+str(con))
                global_and_gate_used_inports = 2

    def terminate_current_or_gate():
        global global_or_gate_idx
        global global_or_gate_used_inports

        if global_or_gate_idx >= 0:
            num_open_ports = 2 - global_or_gate_used_inports
            if num_open_ports > 0:
                log.debug(f"    Terminating OR gate #{global_or_gate_idx}'s {num_open_ports} open input(s)")
                con = [ f"gate_or_{global_or_gate_idx}:A", f"gate_or_{global_or_gate_idx}:B",
                        con_color_termination, default_con_termination_instr ]
                wokwi_design["connections"].append(con)
                log.debug("      Connection: "+str(con))
                global_or_gate_used_inports = 2

    def select_next_or_gate():
        global global_or_gate_idx
        global global_or_gate_used_inports

        global_or_gate_idx += 1
        log.debug(f"    Selected next (non-existing) OR gate #{global_or_gate_idx}")

        global_or_gate_used_inports = 0

    def select_next_and_gate():
        global global_and_gate_idx
        global global_and_gate_used_inports

        global_and_gate_idx += 1
        log.debug(f"    Selected next AND gate #{global_and_gate_idx}")

        global_and_gate_used_inports = 0

    def allocate_next_free_and_gate_inport():
        global global_and_gate_idx
        global global_and_gate_used_inports

        # we need to connect, let's see if we can still use the current gate (check for free input ports)
        if global_and_gate_used_inports >= 2:
            select_next_and_gate()

        retval = (global_and_gate_idx, global_and_gate_used_inports, ['A', 'B'][global_and_gate_used_inports])
        global_and_gate_used_inports += 1

        return retval

    def allocate_next_free_or_gate_inport():
        global global_or_gate_idx
        global global_or_gate_used_inports

        # we need to connect, let's see if we can still use the current gate (check for free input ports)
        if global_or_gate_used_inports >= 2:
            select_next_or_gate()

        retval = (global_or_gate_idx, global_or_gate_used_inports, ['A', 'B'][global_or_gate_used_inports])
        global_or_gate_used_inports += 1

        return retval

    def get_expected_bin_out_vals(output_names, output_data, num_inputs):
        # create binary based expectation values for Arduino verification code
        # see also: https://www.arduino.cc/reference/en/language/variables/constants/integerconstants/
        expected_bin_val = ""
        for k in range(2**num_inputs):
            expected_bin_val += linesep + "    0b"
            for output in output_names:
                expected_bin_val += str(output_data[output][k])
            expected_bin_val += ","

        return expected_bin_val


    log.info(f"Log level: {log_level}")

    if args.parts_only and args.connections_only:
        parser.error("Combination of -p and -c is currently not supported.")

    # ------------------------------------------------------------------------------
    # generate insights about the design input data, i.e. log them to the console
    # ------------------------------------------------------------------------------
    # user specific design definition

    # - asume no duplicate names in use
    # - asume order of output values (zeros and ones) matches binary input order
    #   (e.g. for three inputs: 000, 001, 010, 011, 100, ..., 110, 111)
    # - make input names optional (and use default ones, e.g. 'a', 'b', 'c', ...)

    in_data = {}
    try:
        with open(args.in_file, 'r') as f:
            in_data = json.loads( f.read() )
            log.info(f"Data is read from input file '{args.in_file}'")
    except FileNotFoundError:
        log.error(f"Input file '{args.in_file}' cannot be found. Use flag '-h' to get usage.")
        exit(1)

    # the 'logic' dictionary used within this script defines the
    # - names of the output variables
    # - the list of integers that describe the input combination (row index of the truth table) when the output function is '1'
    # note: the order of key-value entries inside the dictionary is not relevant
    logic = {}

    input_names = in_data["inputs"]
    num_inputs = len(input_names)
    output_names = list( in_data["outputs"].keys() )
    num_outputs = len(output_names)

    log.info(f"Inputs:    {num_inputs:2} {input_names}")
    log.info(f"Outputs:   {num_outputs:2} {output_names}")

    for output in output_names:
        # make sure that we have 2^num_inputs output values!
        assert len(in_data["outputs"][output]) == 2**num_inputs
        ones = [i for i in range(2**num_inputs) if in_data["outputs"][output][i] == 1]
        log.info(f"  Output {output}: {in_data['outputs'][output]}; ones: {ones}")
        logic[output] = ones;

    max_ones_idx = 2**num_inputs - 1
    log.debug(f"Max ones idx: 2^{num_inputs} - 1 = {max_ones_idx}")

    log.debug("Wokwi design (at start):")
    log.debug(wokwi_design)

    # ------------------------------------------------------------------------------
    # reset counters to prepare all the work, create instances, etc. ...

    num_all_buffers = num_inputs + num_outputs
    num_all_not_gates = num_inputs
    num_all_and_gates = 0
    num_all_or_gates = 0

    # maximum number of AND and OR gate stages required (important for the layout)
    num_and_stages_max_overall = 0
    num_or_stages_max_overall = 0

     # keep meta data for resource estimation, etc
    logic_meta = {}

    q = qm.QuineMcCluskey()

    # ------------------------------------------------------------------------------
    # first iteration over all outputs is to show all the CNF terms,
    # to get a part resources estimation;
    # please note that they ae not added to and layed out in the wokwi design yet
    for output in logic:
        # reset estimation counters for the current output
        logic_meta[output] = {
            "qm_terms_raw": [],
            "num_terms": 0, # num_ORed_AND_terms
            "cnf_function": "", # build up string to get a human readable function in conjunctive normal form (CNF)
            "num_and_gates": 0,
            "num_and_gate_stages": [], # for every term
            "num_and_gate_stages_max": 0,
            "and_gates_first_stage": [],
            "inputs_for_first_or_gate_stage": [],
            "or_gates_first_stage": [],
            "final_or_gate": None
        }

        log.debug(f"Running Quine-McCluskey algorithm for output {output}...")
        logic_meta[output]["qm_terms_raw"] = list( q.simplify(logic[output]) ) # convert set into list (to allow indexing)
        log.debug(f"Raw qm terms for {output}: {logic_meta[output]['qm_terms_raw']}")

        # iterate over the terms (those that are OR'ed)
        logic_meta[output]["num_terms"] = len(logic_meta[output]["qm_terms_raw"])

        # iterate over the terms (aka miniterms) for the current output
        cnf_function = ""
        for term_idx in range(logic_meta[output]["num_terms"]):
            cnf_function += sym_term_start

            # iterate over every input variable and see if it is used in the term or not;
            # if it is used check if the negated or original variable is used
            num_inputs_in_term = 0
            for input_idx in range(num_inputs):
                #The next log line give very verbose debugging, comment it out for now
                #log.debug(f"Is input #{input_idx} used in the current term {logic_meta[output]['terms_raw'][term_idx]}? {logic_meta[output]['terms_raw'][term_idx][input_idx]}")
                if logic_meta[output]['qm_terms_raw'][term_idx][input_idx] in ['0', '1']:
                    if num_inputs_in_term > 0:
                        # if another input has been used in the term before, add symbol for AND op
                        cnf_function += sym_and
                    if '0' == logic_meta[output]['qm_terms_raw'][term_idx][input_idx]:
                        # add a prefix to indicate negation
                        cnf_function += sym_negation
                    # if it used negated or un-negated, add the name
                    cnf_function += input_names[input_idx]
                    num_inputs_in_term += 1

            cnf_function += sym_term_end

            (term_num_and_gates, term_num_and_stages) = calc_num_and_gates(num_inputs_in_term)
            logic_meta[output]["num_and_gate_stages"].append(term_num_and_stages)

            # accumulate all AND gates for the output (over all terms for the output)
            logic_meta[output]["num_and_gates"] += term_num_and_gates

            # take maximum of AND stages for the output
            logic_meta[output]["num_and_gate_stages_max"] = max(logic_meta[output]["num_and_gate_stages_max"], term_num_and_stages)

            # leave out the 'or' after last term
            if term_idx < logic_meta[output]["num_terms"]-1:
                cnf_function += sym_or

        # function description in CNF is completed
        logic_meta[output]["cnf_function"] = cnf_function

        # Display CNF term
        log.info(f"Calculated CNF for output {output}: {logic_meta[output]['cnf_function']}")

        log.debug(f"    Number of OR'ed AND-terms: {logic_meta[output]['num_terms']}")

        log.debug(f"    Calculation of output {output} requires {logic_meta[output]['num_and_gates']:3} two-input AND gate(s)")
        log.debug(f"                              in max {logic_meta[output]['num_and_gate_stages_max']:3} stage(s)")

        # not only for this output but for the whole device
        num_and_stages_max_overall = max(num_and_stages_max_overall, logic_meta[output]['num_and_gate_stages_max'])

        # accumulate all AND and all OR gates, not only for the current output but for the whole device
        num_all_and_gates += logic_meta[output]["num_and_gates"]

    log.info("Estimated parts usage:")
    log.info(f"    * {num_all_buffers:3} buffers (for the inputs and the outputs)")
    log.info(f"    * {num_all_not_gates:3} NOT gate(s) (for the negated inputs)")
    log.info(f"    * {num_all_and_gates:3} two-input AND gate(s), in max. {num_and_stages_max_overall} stages")
    log.info(f"    * number of two-input OR gate(s) not estimated yet")

    # ------------------------------------------------------------------------------
    # Create the parts and insert them into the design at start locations
    # that will be modified later on;
    # omit the OR gates

    # No additional NOT gates and buffers expected
    assert num_all_buffers == (num_inputs + num_outputs)
    assert num_all_not_gates == num_inputs

    # Input buffers and NOT gates
    for k in range(num_inputs):
        wokwi_gate_buffer_inst = wokwi_gate_buffer.copy()
        wokwi_gate_buffer_inst["id"] = "input_"+input_names[k]
        wokwi_gate_buffer_inst["top"] = 2*k*wokwi_gate_spacing_v
        wokwi_gate_buffer_inst["left"] = 0
        wokwi_design["parts"].append(wokwi_gate_buffer_inst)

        wokwi_gate_not_inst = wokwi_gate_not.copy()
        wokwi_gate_not_inst["id"] = "input_not_"+input_names[k]
        wokwi_gate_not_inst["top"] = (2*k + 1)*wokwi_gate_spacing_v
        wokwi_gate_not_inst["left"] = 0
        wokwi_design["parts"].append(wokwi_gate_not_inst)

        # directly connect the negated inputs to the buffers of the non-negated inputs
        con = [ f"input_not_{input_names[k]}:IN", f"input_{input_names[k]}:IN",
                con_color_termination, default_con_termination_instr ]
        log.debug("    Connection: "+str(con))
        wokwi_design["connections"].append(con)
    log.debug("Added input buffer and NOT gate parts to the wokwi design")
    log.debug("Also connected their inputs together as they are derived from the same inputs")

    # AND gates
    for k in range(num_all_and_gates):
        wokwi_gate_and_inst = wokwi_gate_and2.copy()
        wokwi_gate_and_inst["id"] = f"gate_and_{k}"
        wokwi_gate_and_inst["top"] = k * wokwi_gate_spacing_v
        wokwi_gate_and_inst["left"] = 2 * wokwi_gate_spacing_h
        wokwi_design["parts"].append(wokwi_gate_and_inst)
    log.debug("Added AND gate parts to the wokwi design")

    # ------------------------------------------------------------------------------
    # second iteration over all outputs is to connect inputs with first stage of AND gates
    log.info("")
    log.info("Connecting inputs with first stage of AND gates for every output.")
    for output in logic:
        log.info(f"Connecting input inside the wokwi design to first AND gate stage (later used for output {output})...")

        # iterate over the terms of the CNF output function
        for term_idx in range(logic_meta[output]["num_terms"]):
            log.debug("---") # we need some visual separator here
            log.debug(f"  Processing first AND stage of term #{term_idx+1} of the CNF function for output {output}...")

            # if the last AND gate has not been fully used, terminate it
            terminate_current_and_gate()

            select_next_and_gate()

            # iterate over every input variable and see if it is used or not;
            # if it is used check if the negated or original variable is used
            current_term_and_gates_for_first_stage = []
            for input_idx in range(num_inputs):

                if logic_meta[output]['qm_terms_raw'][term_idx][input_idx] in ['0', '1']:
                    (and_gate_idx, and_gate_port_idx, and_gate_port_name) = allocate_next_free_and_gate_inport()
                    log.debug(f"    Allocated port #{and_gate_port_idx} ('{and_gate_port_name}') of AND gate #{and_gate_idx}")

                    # put AND gate in a list as reminder to work on them later
                    current_term_and_gates_for_first_stage.append(and_gate_idx)

                    if '0' == logic_meta[output]['qm_terms_raw'][term_idx][input_idx]:
                        log.debug(f"    Use negated input {input_names[input_idx]}")
                        # connect current AND's input port to negated device input
                        con = [ f"input_not_{input_names[input_idx]}:OUT", f"gate_and_{and_gate_idx}:{and_gate_port_name}",
                                con_color_neginput_and, default_con_instr ]
                    else:
                        log.debug(f"    Use input {input_names[input_idx]}")
                        # connect current AND's input port to non-negated device input
                        con = [ f"input_{input_names[input_idx]}:OUT", f"gate_and_{and_gate_idx}:{and_gate_port_name}",
                                con_color_input_and, default_con_instr ]
                    log.debug("      Connection: "+str(con))
                    wokwi_design["connections"].append(con)

            # if the last AND gate has not been fully used (odd number of inputs), terminate it
            terminate_current_and_gate()

            and_gates_used_during_stage = list(set(current_term_and_gates_for_first_stage))

            logic_meta[output]["and_gates_first_stage"].append(and_gates_used_during_stage)

            log.debug(f"  Processing first AND stage of term #{term_idx+1} of the CNF function for output {output} is done and used AND gates {and_gates_used_during_stage}")

        log.info(f"All AND gates required in the first AND gate stage for output {output}: {str(logic_meta[output]['and_gates_first_stage'])}")
        # next loop iteration for the function of the next output
        # ------------------------------------------------------------------------------
    log.info("Connecting inputs with first stage of AND gates for every output completed.")

    # ------------------------------------------------------------------------------
    # third iteration merges all first stage AND gates down to a single 'root'
    # and gate as output of the CNF term -- which then in turn will need to be OR'ed to get the output
    log.info("")
    log.info("Merges all first stage AND gates down to a single 'root' AND gate (for every term of every output)")
    for output in logic:
        and_gates_for_first_or_stage = []

        for current_term_and_gates_for_first_stage in logic_meta[output]['and_gates_first_stage']:
            #log.info(current_term_and_gates_for_first_stage)

            if len(current_term_and_gates_for_first_stage) == 0:
                log.error("Something went wrong with the first stage of AND gates for current term.")
            elif len(current_term_and_gates_for_first_stage) == 1:
                output_and_gates_for_stage = current_term_and_gates_for_first_stage[0]
                log.info(f"Single AND gate #{output_and_gates_for_stage} does not need to be merged.")
                and_gates_for_first_or_stage.append(output_and_gates_for_stage)
            elif len(current_term_and_gates_for_first_stage) > 1:
                log.info(f"Merging AND gates {current_term_and_gates_for_first_stage} down to single AND gate...")

                terminate_current_and_gate()

                # starting point
                input_gates_for_stage = current_term_and_gates_for_first_stage

                log.warning("Entering potential endless loop (trying to merge AND gates)")
                depth = 1
                while True:
                    output_and_gates_for_stage = []

                    for input_gate_for_stage in input_gates_for_stage:
                        (and_gate_idx, and_gate_port_idx, and_gate_port_name) = allocate_next_free_and_gate_inport()

                        if and_gate_port_idx == 0:
                            get_part_by_id(f"gate_and_{and_gate_idx}")["left"] += depth * wokwi_gate_spacing_h

                        # put AND gate in a list as reminder to work on them later
                        output_and_gates_for_stage.append(and_gate_idx)

                        # connect previous AND gate's output to current AND gate's input port
                        con = [ f"gate_and_{input_gate_for_stage}:OUT", f"gate_and_{and_gate_idx}:{and_gate_port_name}",
                                con_color_and_and_interconnect, default_con_instr ]
                        log.debug("    Connection: "+str(con))
                        wokwi_design["connections"].append(con)

                    # remove duplicates
                    output_and_gates_for_stage = list(set(output_and_gates_for_stage))

                    if len(output_and_gates_for_stage) == 1:
                        log.debug(f"  Merged to single AND gate: {output_and_gates_for_stage[0]}")
                        and_gates_for_first_or_stage.append(output_and_gates_for_stage[0])
                        break
                    else:
                        log.debug(f"  Still having more than one AND gate left: {output_and_gates_for_stage}, turning another round")
                        terminate_current_and_gate()
                        depth += 1 # turn another round and keep track of depth for the layout
                        input_gates_for_stage = output_and_gates_for_stage # output of this round is input for next round

        log.info(f"Remaining AND gates (final stage): {and_gates_for_first_or_stage} for the output {output} to be connected to OR gates")
        logic_meta[output]['inputs_for_first_or_gate_stage'] = and_gates_for_first_or_stage
    log.info("Merges of all first stage AND gates down to a single 'root' AND gate completed.")

    # ------------------------------------------------------------------------------
    # fourth iteration creates first stage of OR gates (in order to OR all terms for every output);
    # and connects the AND gate from the previous stage (=the final AND stage) to it
    log.info("")
    log.info("Combining mini terms: Create first stage of OR gates (in order to OR all terms for every output) ")
    log.info("and connect the AND gate from the previous stage (=the final AND stage) to it.")
    for output in logic:
        terminate_current_or_gate()

        select_next_or_gate()

        output_or_gates_for_stage = []

        gates_for_first_stage = logic_meta[output]['inputs_for_first_or_gate_stage']

        if len(gates_for_first_stage) == 0:
            log.error("Something went wrong with the first stage of OR gates for current output.")
        elif len(gates_for_first_stage) == 1:
            log.warning(f"Single mini term for output {output}: AND gate output (AND gate #{gates_for_first_stage[0]})")
            log.warning("Creating a dummy OR gate (which does not need to be then merged down).")

            (or_gate_idx, or_gate_port_idx, or_gate_port_name) = allocate_next_free_or_gate_inport()

            # put OR gate in a list as reminder to work on them later
            output_or_gates_for_stage.append(or_gate_idx)

            # connect AND gate's output port to OR gate's input port
            con = [ f"gate_and_{gates_for_first_stage[0]}:OUT", f"gate_or_{or_gate_idx}:{or_gate_port_name}",
                    con_color_and_or_interconnect, default_con_instr ]
            log.debug("    Connection: "+str(con))
            wokwi_design["connections"].append(con)

            # directly terminate it, as it's only a dummy OR gate (second inport not needed)
            terminate_current_or_gate()

        elif len(gates_for_first_stage) > 1:
            log.info(f"Connecting outputs of AND gates {gates_for_first_stage} to OR gate...")

            output_or_gates_for_stage = []

            for input_gate_for_stage in gates_for_first_stage:
                (or_gate_idx, or_gate_port_idx, or_gate_port_name) = allocate_next_free_or_gate_inport()

                # put OR gate in a list as reminder to work on them later
                output_or_gates_for_stage.append(or_gate_idx)

                # connect AND gate's output port to OR gate's input port
                con = [ f"gate_and_{input_gate_for_stage}:OUT", f"gate_or_{or_gate_idx}:{or_gate_port_name}",
                        con_color_and_or_interconnect, default_con_instr ]
                log.debug("    Connection: "+str(con))
                wokwi_design["connections"].append(con)

                # remove duplicates
                output_or_gates_for_stage = list(set(output_or_gates_for_stage))

        terminate_current_or_gate()

        log.info(f"First stage of OR gates (connected to AND gates): {output_or_gates_for_stage} for output {output}")
        logic_meta[output]['or_gates_first_stage'] = output_or_gates_for_stage
    log.info("Done combining mini terms (AND gates) by first stage of OR gates.")

    # ------------------------------------------------------------------------------
    # fifth iteration merges all first stage OR gates down to a single 'root'
    # OR gate and connect them to the output buffers
    log.info("")
    log.info("Merges all first stage OR gates down to a single 'root' OR gate and connect them to the output buffers")
    max_or_gate_stages = 0
    for output in logic:
        log.info(f"Performing the merges of all OR gates for output {output}")

        final_or_gate_for_output = None

        terminate_current_or_gate()

        # starting point
        input_gates_for_stage = logic_meta[output]['or_gates_first_stage']
        #log.info(logic_meta[output]['or_gates_first_stage'])

        depth = 1
        max_or_gate_stages = max(max_or_gate_stages, depth)

        if not hasattr(input_gates_for_stage, "__len__"):
            input_gates_for_stage = [ input_gates_for_stage ]
            log.warning("input_gates_for_stage is scalar but that should already be handled correctly")

        log.info(f"Number of OR gates to be merged: {len(input_gates_for_stage)}, i.e. {input_gates_for_stage}")

        if len(input_gates_for_stage) == 1:
            log.info("Only single OR gate, therefore directly connect it to the output buffer")
            final_or_gate_for_output = input_gates_for_stage[0]
        else:
            log.warning("Entering potential endless loop (trying to merge OR gates)")
            while True:
                output_or_gates_for_stage = []

                for input_gate_for_stage in input_gates_for_stage:
                    (or_gate_idx, or_gate_port_idx, or_gate_port_name) = allocate_next_free_or_gate_inport()
                    #log.info(f"Allocated OR gate {or_gate_idx}")

                    #if or_gate_port_idx == 0:
                    #    get_part_by_id(f"gate_or_{and_gate_idx}")["left"] += depth * wokwi_gate_spacing_h

                    # put OR gate in a list as reminder to work on them later
                    output_or_gates_for_stage.append(or_gate_idx)

                    # connect previous OR gate's output to current OR gate's input port
                    con = [ f"gate_or_{input_gate_for_stage}:OUT", f"gate_or_{or_gate_idx}:{or_gate_port_name}",
                            con_color_or_or_interconnect, default_con_instr ]
                    log.debug("    Connection: "+str(con))
                    wokwi_design["connections"].append(con)

                # remove duplicates
                output_or_gates_for_stage = list(set(output_or_gates_for_stage))

                if len(output_or_gates_for_stage) == 1:
                    log.debug(f"  Merged to single OR gate: {output_or_gates_for_stage}")
                    final_or_gate_for_output = output_or_gates_for_stage[0]
                    break
                else:
                    log.debug(f"  Still having more than one OR gate left: {output_or_gates_for_stage}, turning another round")
                    terminate_current_and_gate()
                    depth += 1 # turn another round and keep track of depth for the layout
                    max_or_gate_stages = max(max_or_gate_stages, depth)
                    input_gates_for_stage = output_or_gates_for_stage # output of this round is input for next round

        log.info(f"Identified #{final_or_gate_for_output} as final OR gate for the output {output} to be connected to output buffer")

        # stor in meta dictionary
        logic_meta[output]['final_or_gate'] = final_or_gate_for_output

        # connect AND gate's output port to OR gate's input port
        con = [ f"gate_or_{final_or_gate_for_output}:OUT", f"output_{output}:IN",
                con_color_or_output, default_con_instr ]
        log.debug("    Connection: "+str(con))
        wokwi_design["connections"].append(con)

    log.info(f"Max AND gate stages: {num_and_stages_max_overall}")
    log.info(f"Max  OR gate stages: {max_or_gate_stages}")

    # OR gates
    for k in range(global_or_gate_idx+1):
        wokwi_gate_or_inst = wokwi_gate_or2.copy()
        wokwi_gate_or_inst["id"] = f"gate_or_{k}"
        wokwi_gate_or_inst["top"] = k * wokwi_gate_spacing_v
        wokwi_gate_or_inst["left"] = wokwi_gate_and_inst["left"] + num_and_stages_max_overall * wokwi_gate_spacing_h # TODO/FIXME
        wokwi_design["parts"].append(wokwi_gate_or_inst)
    log.debug("Added OR gate parts to the wokwi design")

    # Output buffers
    for k in range(num_outputs):
        wokwi_gate_buffer_inst = wokwi_gate_buffer.copy()
        wokwi_gate_buffer_inst["id"] = "output_"+output_names[k]
        wokwi_gate_buffer_inst["top"] = 2 * k * wokwi_gate_spacing_v # keep some space between outputs
        wokwi_gate_buffer_inst["left"] = wokwi_gate_or_inst["left"] + max_or_gate_stages * wokwi_gate_spacing_h # TODO/FIXME
        wokwi_design["parts"].append(wokwi_gate_buffer_inst)
    log.debug("Added output buffer parts to the wokwi design")

    log.info(f"Finished the wokwi design!")

    if args.tinytapeout and args.test:
        log.warn("Cannot combine flags '--test'/'-t' and '--tinytapeout'/'--tt'. Removing '-tt'.")
        args.tinytapeout = False

    if args.test:
        log.info("Generating verification code and test framework")
        arduino_sketch_template = None
        with open(arduino_sketch_template_file, 'r') as f:
            arduino_sketch = f.read()
        if arduino_sketch:
            # generate the code, then add parts and connections to the wokwi schematic

            # replace the placeholders with actual values
            arduino_sketch = arduino_sketch.replace("{DESIGN_NUM_USED_INPUTS_PH}", f"{num_inputs}u")
            arduino_sketch = arduino_sketch.replace("{DESIGN_NUM_USED_OUTPUTS_PH}", f"{num_outputs}u")
            expected_bin_out_vals = get_expected_bin_out_vals(output_names, in_data["outputs"], num_inputs)
            arduino_sketch = arduino_sketch.replace("{VERIFICATION_EXPECTED_OUT_VALS_PH}", expected_bin_out_vals)

            # TODO: allow to use non-constant values for placeholders by controlling the from the
            #       Python generator (e.g. by adding command line arguments)
            arduino_sketch = arduino_sketch.replace("{VERIFICATION_STOP_ON_ERROR}", "true")
            arduino_sketch = arduino_sketch.replace("{SERIAL_BAUDRATE_PH}", "230400u")
            arduino_sketch = arduino_sketch.replace("{VERIFICATION_SETUP_TIME_MS_PH}", "50u")
            arduino_sketch = arduino_sketch.replace("{VERIFICATION_HOLD_TIME_MS_PH}", "350u")

            # save the generated Arduino sketch
            with open("sketch.ino", 'w') as f:
                f.write(arduino_sketch)

            # add the Arduino MEGA to the wokwi schematic's parts list
            wokwi_design["parts"].append(wokwi_arduino_mega)

            # add the serial monitor to the wokwi schematic
            wokwi_design["serialMonitor"] = {
                "display": "always",
                "newline": "lf"
            }

            # connect design inputs to Arduino outputs
            arduino_mega_outputs = range(2, 11+1)
            out_idx = 0
            for input in input_names:
                con = [ f"mega:{arduino_mega_outputs[out_idx]}", f"input_{input}:IN",
                        con_color_arduino_interconnect, default_con_instr ]
                log.debug("    Connection: "+str(con))
                wokwi_design["connections"].append(con)
                out_idx += 1

            # connect design outputs to Arduino outputs
            arduino_mega_inputs = range(12, 21+1)
            in_idx = 0
            for output in output_names:
                con = [ f"mega:{arduino_mega_inputs[in_idx]}", f"output_{output}:OUT",
                        con_color_arduino_interconnect, default_con_instr ]
                log.debug("    Connection: "+str(con))
                wokwi_design["connections"].append(con)
                in_idx += 1

        else:
            log.error("Unable to open Arduino sketch template file.")

    if args.tinytapeout:
        log.info("Adding parts from template for tinytapeout")

        # add parts to the wokwi schematic's parts list
        wokwi_design["parts"].append(wokwi_dip_switch8)
        wokwi_design["parts"].append(wokwi_clock_generator)
        wokwi_design["parts"].append(wokwi_chip_input_8pins)
        wokwi_design["parts"].append(wokwi_slide_switch)
        wokwi_design["parts"].append(wokwi_pushbutton)

        # TODO/FIXME: move the next two parts to the far right, next to the output buffer of the top-most signal
        wokwi_design["parts"].append(wokwi_chip_output_8pins)
        wokwi_design["parts"].append(wokwi_7segment)

        vcc_btn = wokwi_vcc.copy()
        vcc_btn["id"] = "vcc_btn"
        vcc_btn["top"] = -450
        vcc_btn["left"] = -320
        vcc_dipsw = wokwi_vcc.copy()
        vcc_dipsw["id"] = "vcc_dipsw"
        vcc_dipsw["top"] = -240
        vcc_dipsw["left"] = -420
        wokwi_design["parts"].append(vcc_btn)
        wokwi_design["parts"].append(vcc_dipsw)

        gnd_7seg = wokwi_gnd.copy()
        gnd_7seg["id"] = "gnd_7seg"
        gnd_7seg["top"] = -70
        gnd_7seg["left"] = 1100
        wokwi_design["parts"].append(gnd_7seg)


        # add connections
        for i in range(1, 8+1):
            con = [ "vcc_dipsw:VCC", f"sw1:{i}a", con_color_vcc_interconnect, default_con_instr ]
            log.debug("    Connection: "+str(con))
            wokwi_design["connections"].append(con)

        con = [ "btn1:2.r", "sw2:3", "orange", [ "h90", "*", "v10" ] ]
        log.debug("    Connection: "+str(con))
        wokwi_design["connections"].append(con)

        con = [ "vcc_btn:VCC", "btn1:1.r", con_color_vcc_interconnect, [ "v0" ] ]
        log.debug("    Connection: "+str(con))
        wokwi_design["connections"].append(con)

        con = [ "sw2:1", "clock1:CLK", "green", [ "v0" ] ]
        log.debug("    Connection: "+str(con))
        wokwi_design["connections"].append(con)

        con = [ "sw2:3", "sw1:1b", "violet", [ "v0" ] ]
        log.debug("    Connection: "+str(con))
        wokwi_design["connections"].append(con)

        con = [ "chip1:EXTIN0", "sw2:2", "green", [ "h0", "v-40", "h-20" ] ]
        log.debug("    Connection: "+str(con))
        wokwi_design["connections"].append(con)

        for i in range(2, 8+1):
            con = [ f"chip1:EXTIN{i-1}", f"sw1:{i}b", "violet", [ "h0" ] ]
            log.debug("    Connection: "+str(con))
            wokwi_design["connections"].append(con)

        con = [ "chip2:EXTOUT0", "sevseg1:A", con_color_7seg_interconnect, [ "h21.01", "v-28.8", "h96" ] ]
        log.debug("    Connection: "+str(con))
        wokwi_design["connections"].append(con)
        con = [ "chip2:EXTOUT1", "sevseg1:B", con_color_7seg_interconnect, [ "h11.41", "v-48", "h115.2", "v38.4" ] ]
        log.debug("    Connection: "+str(con))
        wokwi_design["connections"].append(con)
        con = [ "chip2:EXTOUT2", "sevseg1:C", con_color_7seg_interconnect, [ "h30.61", "v-38.4", "h115.2", "v105.6", "h-28.8" ] ]
        log.debug("    Connection: "+str(con))
        wokwi_design["connections"].append(con)
        con = [ "chip2:EXTOUT3", "sevseg1:D", con_color_7seg_interconnect, [ "h49.81", "v57.6", "h48" ] ]
        log.debug("    Connection: "+str(con))
        wokwi_design["connections"].append(con)
        con = [ "chip2:EXTOUT4", "sevseg1:E", con_color_7seg_interconnect, [ "v9.6", "h-48", "v-38.4" ] ]
        log.debug("    Connection: "+str(con))
        wokwi_design["connections"].append(con)
        con = [ "chip2:EXTOUT5", "sevseg1:F", con_color_7seg_interconnect, [ "h69.01", "v-57.6", "h28.8" ] ]
        log.debug("    Connection: "+str(con))
        wokwi_design["connections"].append(con)
        con = [ "chip2:EXTOUT6", "sevseg1:G", con_color_7seg_interconnect, [ "h78.61", "v-57.6" ] ]
        log.debug("    Connection: "+str(con))
        wokwi_design["connections"].append(con)
        con = [ "chip2:EXTOUT7", "sevseg1:DP", con_color_7seg_interconnect, [ "v28.8", "h136.21" ] ]
        log.debug("    Connection: "+str(con))
        wokwi_design["connections"].append(con)
        con = [ "chip2:EXTOUT7", "sevseg1:DP", con_color_7seg_interconnect, [ "v28.8", "h136.21" ] ]
        log.debug("    Connection: "+str(con))
        wokwi_design["connections"].append(con)
        con = [ "gnd_7seg:GND", "sevseg1:COM.1", con_color_gnd_interconnect, [ "v0" ] ]
        log.debug("    Connection: "+str(con))
        wokwi_design["connections"].append(con)

        # Check number of inputs
        if num_inputs > 8:
            log.warn("Won't be able to connect more than 8 inputs!")
            num_inputs = 8

        for k in range(num_inputs):
            con = [ f"chip1:IN{k}", "input_"+input_names[k]+":IN", con_color_board_interconnect, default_con_instr ]
            log.debug("    Connection: "+str(con))
            wokwi_design["connections"].append(con)

        # Check number of outputs
        if num_outputs > 8:
            log.warn("Won't be able to connect more than 8 outputs!")
            num_outputs = 8

        for k in range(num_outputs):
            con = [ "output_"+output_names[k]+":OUT", f"chip2:OUT{k}", con_color_board_interconnect, default_con_instr ]
            log.debug("    Connection: "+str(con))
            wokwi_design["connections"].append(con)

    #log.debug( json.dumps(logic_meta, indent=4) )

    wokwi_design_dump = wokwi_design

    # limit the dump; mutual exclusion of both options has been guaranteed earlier
    if args.parts_only:
        log.info("Only dumping wokwi parts.")
        wokwi_design_dump = wokwi_design["parts"]
    elif args.connections_only:
        log.info("Only dumping wokwi connections.")
        wokwi_design_dump = wokwi_design["connections"]

    if args.out_file:
        log.info(f"Writing final wokwi design file '{args.out_file}'...")
        with open(args.out_file, 'w') as f:
            json.dump(wokwi_design_dump, f, indent=4)
    else:
        log.info("Dumping final wokwi design to stdout...")
        print( json.dumps(wokwi_design_dump, indent=4) )
