from drafter import *
from dataclasses import dataclass, field
import math


# ==========================================
# DATACLASSES
# ==========================================

@dataclass
class GearCalculation:
    name: str
    driver_teeth: int
    driven_teeth: int
    input_rpm: float
    input_torque: float


@dataclass
class State:
    history: list[GearCalculation] = field(default_factory=list)
    selected_name: str = ""
    comparison_name: str = ""
    display_mode: str = "Detailed"
    show_formulas: str = "Yes"

    # Remember the user's calculator inputs
    gear_name: str = "System"
    driver_input: str = ""
    driven_input: str = ""
    rpm_input: str = ""
    torque_input: str = ""


# ==========================================
# CALCULATION FUNCTIONS
# ==========================================

def gear_ratio(gear: GearCalculation) -> float:
    return gear.driven_teeth / gear.driver_teeth


def output_rpm(gear: GearCalculation) -> float:
    return gear.input_rpm / gear_ratio(gear)


def output_torque(gear: GearCalculation) -> float:
    return gear.input_torque * gear_ratio(gear)


def find_gear(state: State, name: str):
    for gear in state.history:
        if gear.name == name:
            return gear
    return None


# ==========================================
# NAVIGATION - UPDATED
# ==========================================

def navigation():
    return [
        LineBreak(),
        HorizontalRule(),
        Link("Home", "index"),
        " | ",
        Link("Calculator", "calculator"),
        " | ",
        Link("History", "history"),
        " | ",
        Link("Compare", "compare"),
        " | ",
        Link("Guide", "guide"),
        " | ",
        Link("Settings", "settings")
    ]

# ==========================================
# DISPLAY HELPERS
# ==========================================

def gear_summary(gear: GearCalculation):
    return [
        Header(gear.name),
        "Gear Ratio: " +
        str(round(gear_ratio(gear), 2)) + ":1\n",

        "Output RPM: " +
        str(round(output_rpm(gear), 2)) + "\n",

        "Ideal Output Torque: " +
        str(round(output_torque(gear), 2)) + " N-m\n"
    ]


def error_page(state: State, title: str, message: str) -> Page:
    return Page(state, [
        Header(title),
        message,
        "\nYour previous inputs have been saved.\n",
        Button("Try Again", "calculator"),
        *navigation()
    ])


# ==========================================
# ROUTE 1: HOME
# ==========================================

@route
def index(state: State) -> Page:
    return Page(state, [
        Header("MechTools"),
        "Welcome to the Gear Ratio Calculator!\n",
        "Calculate gear ratios, output speed, and torque.\n",

        "Saved calculations: " +
        str(len(state.history)) + "\n",

        Button("Get Started", "calculator"),
        *navigation()
    ])


# ==========================================
# ROUTE 2: CALCULATOR
# ==========================================

@route
def calculator(state: State) -> Page:
    return Page(state, [
        Header("Gear Calculator"),

        "Gear system name:",
        TextBox("name", state.gear_name),

        "Driver gear teeth:",
        TextBox("driver_teeth", state.driver_input),

        "Driven gear teeth:",
        TextBox("driven_teeth", state.driven_input),

        "Input speed (RPM):",
        TextBox("input_rpm", state.rpm_input),

        "Input torque (N-m):",
        TextBox("input_torque", state.torque_input),

        Button("Calculate and Save", "calculate"),
        *navigation()
    ])


# ==========================================
# ROUTE 3: CALCULATE AND VALIDATE
# ==========================================

@route
def calculate(state: State, name: str,
              driver_teeth: str, driven_teeth: str,
              input_rpm: str, input_torque: str) -> Page:

    # Save everything the user typed BEFORE checking errors
    state.gear_name = name
    state.driver_input = driver_teeth
    state.driven_input = driven_teeth
    state.rpm_input = input_rpm
    state.torque_input = input_torque

    # ERROR 1: Missing information
    if (name.strip() == "" or
        driver_teeth.strip() == "" or
        driven_teeth.strip() == "" or
        input_rpm.strip() == "" or
        input_torque.strip() == ""):

        return error_page(
            state,
            "Missing Information",
            "Please fill in all fields before calculating."
        )

    # ERROR 2: Invalid numbers
    try:
        driver_teeth = int(driver_teeth)
        driven_teeth = int(driven_teeth)
        input_rpm = float(input_rpm)
        input_torque = float(input_torque)

    except ValueError:
        return error_page(
            state,
            "Invalid Input",
            "Please enter valid numbers. Gear teeth must be whole numbers."
        )

    # ERROR 3: Zero or negative gear teeth
    if driver_teeth <= 0 or driven_teeth <= 0:
        return error_page(
            state,
            "Invalid Gear Sizes",
            "Both gears must have more than zero teeth."
        )

    # ERROR 4: Extremely large gear sizes
    if driver_teeth > 10000 or driven_teeth > 10000:
        return error_page(
            state,
            "Invalid Gear Size",
            "Please enter no more than 10,000 teeth per gear."
        )

    # ERROR 5: NaN or infinity
    if (not math.isfinite(input_rpm) or
        not math.isfinite(input_torque)):

        return error_page(
            state,
            "Invalid Number",
            "Please enter finite numbers for RPM and torque."
        )

    # ERROR 6: Negative RPM or torque
    if input_rpm < 0 or input_torque < 0:
        return error_page(
            state,
            "Invalid Input",
            "RPM and torque cannot be negative."
        )

    # ERROR 7: Extremely large RPM or torque
    if input_rpm > 1000000000 or input_torque > 1000000000:
        return error_page(
            state,
            "Input Too Large",
            "RPM and torque must be no more than one billion."
        )

    # ERROR 8: Duplicate names
    name = name.strip()

    if find_gear(state, name) is not None:
        return error_page(
            state,
            "Name Already Used",
            "Please choose a different name for this gear system."
        )

    # All inputs are valid
    gear = GearCalculation(
        name,
        driver_teeth,
        driven_teeth,
        input_rpm,
        input_torque
    )

    state.history.append(gear)
    state.selected_name = name

    return results(state)


# ==========================================
# ROUTE 4: RESULTS
# ==========================================

@route
def results(state: State) -> Page:

    gear = find_gear(state, state.selected_name)

    if gear is None:
        return Page(state, [
            Header("No Calculation Selected"),
            "Please calculate a gear system first.",
            Button("Open Calculator", "calculator"),
            *navigation()
        ])

    content = [
        Header("Calculation Results"),
        Header(gear.name),

        "Gear Ratio: " +
        str(round(gear_ratio(gear), 2)) + ":1\n",

        "Output RPM: " +
        str(round(output_rpm(gear), 2)) + "\n",

        "Ideal Output Torque: " +
        str(round(output_torque(gear), 2)) + " N-m\n"
    ]

    # Detailed mode displays extra explanations
    if state.display_mode == "Detailed":

        if gear_ratio(gear) > 1:
            content.append(
                "This system reduces speed and increases ideal torque.\n"
            )

        elif gear_ratio(gear) < 1:
            content.append(
                "This system increases speed and reduces ideal torque.\n"
            )

        else:
            content.append(
                "This system has a 1:1 gear ratio.\n"
            )

        if state.show_formulas == "Yes":
            content.extend([
                Header("Formulas Used"),
                "Gear Ratio = Driven Teeth / Driver Teeth\n",
                "Output RPM = Input RPM / Gear Ratio\n",
                "Ideal Output Torque = Input Torque * Gear Ratio\n"
            ])

    content.extend([
        "Calculations assume two external gears without losses.\n",
        Button("Calculate Another", "calculator"),
        *navigation()
    ])

    return Page(state, content)


# ==========================================
# ROUTE 5: HISTORY
# ==========================================

@route
def history(state: State) -> Page:

    content = [Header("Saved Calculations")]

    if len(state.history) == 0:
        content.append(
            "No calculations have been saved yet."
        )

    else:
        names = []

        for gear in state.history:
            content.extend(gear_summary(gear))
            names.append(gear.name)

        content.extend([
            Header("Delete a Calculation"),
            "Choose the calculation to delete:",
            SelectBox("name", names),
            Button("Delete Calculation", "delete_record")
        ])

    content.extend(navigation())
    return Page(state, content)


# ==========================================
# ROUTE 6: DELETE CALCULATION
# ==========================================

@route
def delete_record(state: State, name: str) -> Page:

    updated_history = []

    for gear in state.history:
        if gear.name != name:
            updated_history.append(gear)

    state.history = updated_history

    if state.selected_name == name:
        state.selected_name = ""

    if state.comparison_name == name:
        state.comparison_name = ""

    return history(state)


# ==========================================
# ROUTE 7: COMPARISON
# ==========================================

@route
def compare(state: State) -> Page:

    content = [Header("Compare Gear Systems")]

    if len(state.history) < 2:
        content.append(
            "Please save at least two calculations before comparing."
        )

    else:
        names = []

        for gear in state.history:
            names.append(gear.name)

        content.extend([
            "Select the first gear system:",
            SelectBox("first_name", names),

            "Select the second gear system:",
            SelectBox("second_name", names),

            Button("Compare", "compare_results")
        ])

    content.extend(navigation())
    return Page(state, content)


# ==========================================
# ROUTE 8: COMPARISON RESULTS
# ==========================================

@route
def compare_results(state: State,
                    first_name: str,
                    second_name: str) -> Page:

    first = find_gear(state, first_name)
    second = find_gear(state, second_name)

    if first is None or second is None:
        return Page(state, [
            Header("Comparison Error"),
            "One or both calculations could not be found.",
            Button("Try Again", "compare"),
            *navigation()
        ])

    if first_name == second_name:
        return Page(state, [
            Header("Choose Different Systems"),
            "Please select two different gear systems.",
            Button("Try Again", "compare"),
            *navigation()
        ])

    state.selected_name = first_name
    state.comparison_name = second_name

    content = [
        Header("Gear Comparison"),
        *gear_summary(first),
        *gear_summary(second)
    ]

    if output_rpm(first) > output_rpm(second):
        content.append(
            first.name + " has the higher output RPM.\n"
        )

    elif output_rpm(first) < output_rpm(second):
        content.append(
            second.name + " has the higher output RPM.\n"
        )

    else:
        content.append(
            "Both systems have the same output RPM.\n"
        )

    if output_torque(first) > output_torque(second):
        content.append(
            first.name + " has the higher ideal output torque.\n"
        )

    elif output_torque(first) < output_torque(second):
        content.append(
            second.name + " has the higher ideal output torque.\n"
        )

    else:
        content.append(
            "Both systems have the same ideal output torque.\n"
        )

    content.extend([
        Button("Compare Again", "compare"),
        *navigation()
    ])

    return Page(state, content)


# ==========================================
# ROUTE 9: FORMULA GUIDE
# ==========================================

@route
def guide(state: State) -> Page:

    return Page(state, [
        Header("Engineering Formula Guide"),

        Header("Gear Ratio"),
        "Gear Ratio = Driven Teeth / Driver Teeth\n",

        Header("Output Speed"),
        "Output RPM = Input RPM / Gear Ratio\n",

        Header("Output Torque"),
        "Ideal Output Torque = Input Torque * Gear Ratio\n",

        Header("Example"),
        "Driver Gear: 20 teeth\n",
        "Driven Gear: 60 teeth\n",
        "Input Speed: 1200 RPM\n",
        "Input Torque: 10 N-m\n",

        "Gear Ratio: 3:1\n",
        "Output Speed: 400 RPM\n",
        "Ideal Output Torque: 30 N-m\n",

        "These formulas apply to a two-gear ideal system.\n",

        *navigation()
    ])


# ==========================================
# ROUTE 10: SETTINGS
# ==========================================

@route
def settings(state: State) -> Page:

    return Page(state, [
        Header("Settings"),

        "Results display mode:",
        SelectBox(
            "display_mode",
            ["Detailed", "Simple"],
            state.display_mode
        ),

        "Show formulas on detailed results?",
        SelectBox(
            "show_formulas",
            ["Yes", "No"],
            state.show_formulas
        ),

        Button("Save Settings", "save_settings"),
        *navigation()
    ])


# ==========================================
# ROUTE 11: SAVE SETTINGS
# ==========================================

@route
def save_settings(state: State,
                  display_mode: str,
                  show_formulas: str) -> Page:

    state.display_mode = display_mode
    state.show_formulas = show_formulas

    return Page(state, [
        Header("Settings Saved"),

        "Display Mode: " + state.display_mode + "\n",
        "Show Formulas: " + state.show_formulas + "\n",

        Button("Back to Settings", "settings"),
        *navigation()
    ])


# ==========================================
# START WEBSITE
# ==========================================

start_server(State())

