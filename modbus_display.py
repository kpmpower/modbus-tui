#!/usr/bin/env python3

# from rich.console import Console
import random
from time import sleep

from rich import box
from rich.layout import Layout
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.live import Live
from rich.text import Text

MODBUS_ENABLE = False

if MODBUS_ENABLE:
    import modbus_client as mb

# COLORS
TITLE_COLOR = "bold red"
VALUE_LABEL_COLOR = "bold green"
VOLT_MAX_COLOR = "bold magenta"
TEMPERATURE_MAX_COLOR = "bold green"
VOLT_COLOR = "dim magenta"
TEMPERATURE_COLOR = "dim green"
STATE_COLOR = "cyan"
ERROR_STATE_COLOR = "plum4"

# console = Console()
layout = Layout()

values = {
    "monoblock_voltages": [random.randrange(5005,10015) for i in range(38)],
    "monoblock_temperatures": [random.randrange(5005,10015) for i in range(38)],
    "system_voltages": [random.randrange(5005,10015) for i in range(38)],
    "system_temperatures": [random.randrange(5005,10015) for i in range(38)],
    "system_currents": [random.randrange(5005,10015) for i in range(38)],
    "system_health": [random.randrange(5005,10015) for i in range(38)],
    "system_booleans": [random.randrange(5005,10015) for i in range(38)],
    "errors": [random.randrange(5005,10015) for i in range(38)],
}


def add_color(string, color):
    text = "[" + color + "]" + str(string) + "[/" + color + "]"
    return text

def new_line(number):
    return "\n" * number

def update_system_voltages(dictionary):
    # text = Text("Voltages\n", style="bold red", justify="center")
    arr1 = dictionary["system_voltages"]
    arr2 = dictionary["system_currents"]
    arr = Text.assemble(
        (" VOLTAGES", TITLE_COLOR), new_line(1),
        (" System Voltage:   ", VALUE_LABEL_COLOR), str(arr1[0]/10.0), (" V", "white"), new_line(1),
        (" Inverter Voltage: ", VALUE_LABEL_COLOR), str(arr1[1]/10.0), (" V", "white"), new_line(1),
        (" PSU Voltage:      ", VALUE_LABEL_COLOR), str(arr1[2]/10.0), (" V", "white"), new_line(3),
        (" CURRENTS", TITLE_COLOR), new_line(1),
        (" System Current:   ", VALUE_LABEL_COLOR), str(arr2[0]/10.0 - 1600), (" A", "white"), new_line(1),
        (" Hall Current:     ", VALUE_LABEL_COLOR), str(arr2[1]/10.0 - 1600), (" A", "white"), new_line(1),
        (" Shunt Current:    ", VALUE_LABEL_COLOR), str(arr2[2]/10.0 - 1600), (" A", "white"), new_line(1))
    return Panel(arr)

def parse_system_state(val):
    if val == 0:
        text = "Standby"
        color = STATE_COLOR
    elif val == 1:
        text = "Charge"
        color = STATE_COLOR
    elif val == 2:
        text = "Discharge"
        color = STATE_COLOR
    elif val == 3:
        text = "EOD"
        color = STATE_COLOR
    elif val == 4:
        text = "Service"
        color = STATE_COLOR
    elif val == 5:
        text = "Pre-Standby"
        color = STATE_COLOR
    else:
        text = "Error"
        color = ERROR_STATE_COLOR
    return text, color

def update_system_health(dictionary):
    system_health = dictionary["system_health"]
    state, state_color = parse_system_state(system_health[2])
    arr = Text.assemble(
        (" SYSTEM HEALTH", TITLE_COLOR), new_line(1),
        (" System Status:   ", VALUE_LABEL_COLOR), new_line(1),
        (" System State:    ", VALUE_LABEL_COLOR), (state, state_color), new_line(2),
        (" SOC:             ", VALUE_LABEL_COLOR), (str(system_health[0]) + " %", TEMPERATURE_MAX_COLOR), new_line(1),
        (" SOH:             ", VALUE_LABEL_COLOR), (str(system_health[1]) + " %", TEMPERATURE_MAX_COLOR), new_line(1),
    )
    return Panel(arr)


def find_max_value(arr, arr_type):
    max_value = max(arr)
    max_index = arr.index(max_value)
    arr_return = [None for x in range(len(arr))]
    for i, blah in enumerate(arr):
        if arr_type == "voltages":
            val = float(arr[i])
            val = val/1000.0
            if i == max_index:
                arr_return[i] = add_color(val, VOLT_MAX_COLOR)
            else:
                arr_return[i] = add_color(val, VOLT_COLOR)
        elif arr_type == "temperatures":
            val = arr[i] - 40
            if i == max_index:
                arr_return[i] = add_color(val, TEMPERATURE_MAX_COLOR)
            else:
                arr_return[i] = add_color(val, TEMPERATURE_COLOR)
        else:
            pass
    return arr_return

def update_table(dictionary):
    voltages = dictionary["monoblock_voltages"]
    voltages_converted = find_max_value(voltages, "voltages")
    temperatures = dictionary["monoblock_temperatures"]
    temperatures_converted = find_max_value(temperatures, "temperatures")
    table = Table(show_header=True,
                  title="Values",
                  header_style="bold magenta",
                  box=box.ROUNDED)
    table.add_column("BATTERY", style="bold")
    table.add_column("VOLTAGE", min_width=15)
    table.add_column("TEMPERATURE", min_width=15)
    for i, value in enumerate(voltages_converted):
        table.add_row(str(i+1), str(value), str(temperatures_converted[i]))
    return table

def update_modbus(dictionary):
    dictionary["monoblock_voltages"] = mb.monoblock_voltages()
    dictionary["monoblock_temperatures"] = mb.monoblock_temperatures()
    dictionary["system_voltages"] = mb.system_values()
    dictionary["system_currents"] = mb.system_currents()
    dictionary["system_health"] = mb.system_health()

header_style1 = Style(color="red", bold=True)
header_panel = Panel("[green]Anzen BMS Modbus Interpreter",
             style=header_style1)
layout.split_column(
    Layout(header_panel, name="header", size=3),
    Layout(name="upper"),
)

layout["upper"].split_row(
    Layout(Panel(update_table(values), title="Values")),
    Layout(name="right"),
)

layout["right"].split_column(
    Layout(name="right-top"),
    Layout(name="right-middle"),
    Layout(name="right-bottom"),
)

layout["right-top"].split_row(
    Layout(update_system_voltages(values)),
    Layout(update_system_health(values), name="right"),
)

with Live(layout, screen=True) as live:
    while True:
        sleep(1)
        # live.update(make_layout(values))
