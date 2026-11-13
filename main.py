from bakery import assert_equal
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
# MECHTOOLS V.1 - UNIT TESTS
# ==========================================

# ==========================================
# TEST 1: GEAR RATIO
# ==========================================

gear1 = GearCalculation("Test1", 20, 60, 1200, 10)
gear2 = GearCalculation("Test2", 60, 20, 1200, 10)
gear3 = GearCalculation("Test3", 50, 50, 1000, 5)

assert_equal(gear_ratio(gear1), 3.0)
assert_equal(round(gear_ratio(gear2), 2), 0.33)
assert_equal(gear_ratio(gear3), 1.0)

# ==========================================
# TEST 2: OUTPUT RPM
# ==========================================

assert_equal(output_rpm(gear1), 400.0)
assert_equal(output_rpm(gear2), 3600.0)
assert_equal(output_rpm(gear3), 1000.0)

# Regression test for the division-by-zero bug
gear_small = GearCalculation("Small", 1000, 1, 1200, 10)
assert_equal(output_rpm(gear_small), 1200000.0)

# ==========================================
# TEST 3: OUTPUT TORQUE
# ==========================================

assert_equal(output_torque(gear1), 30.0)
assert_equal(round(output_torque(gear2), 2), 3.33)
assert_equal(output_torque(gear3), 5.0)

# ==========================================
# TEST 4: FIND GEAR
# ==========================================

test_state = State()
test_state.history.append(gear1)
test_state.history.append(gear2)

assert_equal(find_gear(test_state, "Test1"), gear1)
assert_equal(find_gear(test_state, "Test2"), gear2)
assert_equal(find_gear(test_state, "Missing"), None)

# ==========================================
# TEST 5: NAVIGATION
# ==========================================

nav = navigation()

assert_equal(nav[2], Link("Home", "index"))
assert_equal(nav[4], Link("Calculator", "calculator"))
assert_equal(nav[6], Link("History", "history"))
assert_equal(nav[8], Link("Compare", "compare"))
assert_equal(nav[10], Link("Guide", "guide"))
assert_equal(nav[12], Link("Settings", "settings"))

# ==========================================
# TEST 6: GEAR SUMMARY
# ==========================================

summary = gear_summary(gear1)

assert_equal(summary[0], Header("Test1"))
assert_equal(summary[1], "Gear Ratio: 3.0:1\n")
assert_equal(summary[2], "Output RPM: 400.0\n")
assert_equal(summary[3], "Ideal Output Torque: 30.0 N-m\n")

# ==========================================
# TEST 7: ERROR PAGE
# ==========================================

test_state = State()

error_result = error_page(
    test_state,
    "Test Error",
    "Something went wrong."
)

assert_equal(error_result.state, test_state)
assert_equal(error_result.content[0], Header("Test Error"))
assert_equal(
    error_result.content[1],
    "Something went wrong."
)
assert_equal(
    error_result.content[3],
    Button("Try Again", "calculator")
)

# ==========================================
# TEST 8: HOME PAGE
# ==========================================

test_state = State()
home_page = index(test_state)

assert_equal(home_page.state, test_state)
assert_equal(home_page.content[0], Header("MechTools"))
assert_equal(
    home_page.content[3],
    "Saved calculations: 0\n"
)

test_state.history.append(gear1)
home_page = index(test_state)

assert_equal(
    home_page.content[3],
    "Saved calculations: 1\n"
)

# ==========================================
# TEST 9: CALCULATOR PAGE
# ==========================================

test_state = State()
calculator_page = calculator(test_state)

assert_equal(
    calculator_page.content[0],
    Header("Gear Calculator")
)

assert_equal(
    calculator_page.content[2],
    TextBox("name", "System")
)

assert_equal(
    calculator_page.content[4],
    TextBox("driver_teeth", "")
)

# FIX: Button is at index 11, not 12.
assert_equal(
    calculator_page.content[11],
    Button("Calculate and Save", "calculate")
)

# ==========================================
# TEST 10: CALCULATE - VALID INPUT
# ==========================================

test_state = State()

result = calculate(
    test_state,
    "Gear A",
    "20",
    "60",
    "1200",
    "10"
)

assert_equal(len(test_state.history), 1)
assert_equal(test_state.history[0].name, "Gear A")
assert_equal(test_state.history[0].driver_teeth, 20)
assert_equal(test_state.history[0].driven_teeth, 60)
assert_equal(test_state.selected_name, "Gear A")
assert_equal(test_state.gear_name, "Gear A")
assert_equal(test_state.driver_input, "20")
assert_equal(test_state.driven_input, "60")
assert_equal(test_state.rpm_input, "1200")
assert_equal(test_state.torque_input, "10")

# ==========================================
# TEST 11: CALCULATE - MISSING INPUT
# ==========================================

test_state = State()

result = calculate(
    test_state,
    "Gear B",
    "",
    "60",
    "1200",
    "10"
)

assert_equal(
    result.content[0],
    Header("Missing Information")
)

assert_equal(len(test_state.history), 0)
assert_equal(test_state.gear_name, "Gear B")
assert_equal(test_state.driver_input, "")

# ==========================================
# TEST 12: CALCULATE - INVALID NUMBERS
# ==========================================

test_state = State()

result = calculate(
    test_state,
    "Gear C",
    "abc",
    "60",
    "1200",
    "10"
)

assert_equal(
    result.content[0],
    Header("Invalid Input")
)
assert_equal(len(test_state.history), 0)

# ==========================================
# TEST 13: CALCULATE - ZERO TEETH
# ==========================================

test_state = State()

result = calculate(
    test_state,
    "Gear D",
    "0",
    "60",
    "1200",
    "10"
)

assert_equal(
    result.content[0],
    Header("Invalid Gear Sizes")
)
assert_equal(len(test_state.history), 0)

# ==========================================
# TEST 14: CALCULATE - NEGATIVE TEETH
# ==========================================

test_state = State()

result = calculate(
    test_state,
    "Gear E",
    "-20",
    "60",
    "1200",
    "10"
)

assert_equal(
    result.content[0],
    Header("Invalid Gear Sizes")
)

# ==========================================
# TEST 15: CALCULATE - LARGE GEARS
# ==========================================

test_state = State()

result = calculate(
    test_state,
    "Gear F",
    "10001",
    "60",
    "1200",
    "10"
)

assert_equal(
    result.content[0],
    Header("Invalid Gear Size")
)

# ==========================================
# TEST 16: CALCULATE - INFINITY
# ==========================================

test_state = State()

result = calculate(
    test_state,
    "Gear G",
    "20",
    "60",
    "inf",
    "10"
)

assert_equal(
    result.content[0],
    Header("Invalid Number")
)

# ==========================================
# TEST 17: CALCULATE - NEGATIVE RPM
# ==========================================

test_state = State()

result = calculate(
    test_state,
    "Gear H",
    "20",
    "60",
    "-1200",
    "10"
)

assert_equal(
    result.content[0],
    Header("Invalid Input")
)

# ==========================================
# TEST 18: CALCULATE - LARGE RPM
# ==========================================

test_state = State()

result = calculate(
    test_state,
    "Gear I",
    "20",
    "60",
    "1000000001",
    "10"
)

assert_equal(
    result.content[0],
    Header("Input Too Large")
)

# ==========================================
# TEST 19: CALCULATE - DUPLICATE NAME
# ==========================================

test_state = State()

calculate(
    test_state,
    "Same",
    "20",
    "60",
    "1200",
    "10"
)

result = calculate(
    test_state,
    "Same",
    "30",
    "90",
    "1500",
    "15"
)

assert_equal(
    result.content[0],
    Header("Name Already Used")
)
assert_equal(len(test_state.history), 1)

# ==========================================
# TEST 20: RESULTS PAGE
# ==========================================

test_state = State()
test_state.history.append(gear1)
test_state.selected_name = "Test1"

result = results(test_state)

assert_equal(
    result.content[0],
    Header("Calculation Results")
)
assert_equal(
    result.content[1],
    Header("Test1")
)
assert_equal(
    result.content[2],
    "Gear Ratio: 3.0:1\n"
)
assert_equal(
    result.content[3],
    "Output RPM: 400.0\n"
)

# ==========================================
# TEST 21: RESULTS - NO SELECTION
# ==========================================

test_state = State()
result = results(test_state)

assert_equal(
    result.content[0],
    Header("No Calculation Selected")
)

# ==========================================
# TEST 22: HISTORY PAGE - EMPTY
# ==========================================

test_state = State()
result = history(test_state)

assert_equal(
    result.content[0],
    Header("Saved Calculations")
)
assert_equal(
    result.content[1],
    "No calculations have been saved yet."
)

# ==========================================
# TEST 23: HISTORY PAGE - SAVED
# ==========================================

test_state = State()
test_state.history.append(gear1)

result = history(test_state)

assert_equal(
    result.content[0],
    Header("Saved Calculations")
)
assert_equal(
    result.content[1],
    Header("Test1")
)

# ==========================================
# TEST 24: DELETE CALCULATION
# ==========================================

test_state = State()
test_state.history.append(gear1)
test_state.history.append(gear2)
test_state.selected_name = "Test1"

result = delete_record(test_state, "Test1")

assert_equal(len(test_state.history), 1)
assert_equal(test_state.history[0].name, "Test2")
assert_equal(test_state.selected_name, "")
assert_equal(
    result.content[0],
    Header("Saved Calculations")
)

# ==========================================
# TEST 25: COMPARE - NOT ENOUGH GEARS
# ==========================================

test_state = State()
result = compare(test_state)

assert_equal(
    result.content[0],
    Header("Compare Gear Systems")
)
assert_equal(
    result.content[1],
    "Please save at least two calculations before comparing."
)

# ==========================================
# TEST 26: COMPARE PAGE - TWO GEARS
# ==========================================

test_state = State()
test_state.history.append(gear1)
test_state.history.append(gear2)

result = compare(test_state)

assert_equal(
    result.content[0],
    Header("Compare Gear Systems")
)
assert_equal(
    result.content[2],
    SelectBox("first_name", ["Test1", "Test2"])
)
assert_equal(
    result.content[4],
    SelectBox("second_name", ["Test1", "Test2"])
)

# ==========================================
# TEST 27: COMPARISON RESULTS
# ==========================================

test_state = State()
test_state.history.append(gear1)
test_state.history.append(gear2)

result = compare_results(
    test_state,
    "Test1",
    "Test2"
)

assert_equal(
    result.content[0],
    Header("Gear Comparison")
)
assert_equal(test_state.selected_name, "Test1")
assert_equal(test_state.comparison_name, "Test2")

# ==========================================
# TEST 28: COMPARE - SAME GEAR
# ==========================================

test_state = State()
test_state.history.append(gear1)

result = compare_results(
    test_state,
    "Test1",
    "Test1"
)

assert_equal(
    result.content[0],
    Header("Choose Different Systems")
)

# ==========================================
# TEST 29: COMPARE - MISSING GEAR
# ==========================================

test_state = State()
test_state.history.append(gear1)

result = compare_results(
    test_state,
    "Test1",
    "Missing"
)

assert_equal(
    result.content[0],
    Header("Comparison Error")
)

# ==========================================
# TEST 30: FORMULA GUIDE
# ==========================================

test_state = State()
result = guide(test_state)

assert_equal(
    result.content[0],
    Header("Engineering Formula Guide")
)
assert_equal(
    result.content[1],
    Header("Gear Ratio")
)
assert_equal(
    result.content[2],
    "Gear Ratio = Driven Teeth / Driver Teeth\n"
)

# ==========================================
# TEST 31: SETTINGS PAGE
# ==========================================

test_state = State()
result = settings(test_state)

assert_equal(
    result.content[0],
    Header("Settings")
)
assert_equal(
    result.content[2],
    SelectBox(
        "display_mode",
        ["Detailed", "Simple"],
        "Detailed"
    )
)

# ==========================================
# TEST 32: SAVE SETTINGS
# ==========================================

test_state = State()

result = save_settings(
    test_state,
    "Simple",
    "No"
)

assert_equal(test_state.display_mode, "Simple")
assert_equal(test_state.show_formulas, "No")

assert_equal(
    result.content[0],
    Header("Settings Saved")
)
assert_equal(
    result.content[1],
    "Display Mode: Simple\n"
)

# ==========================================
# END OF UNIT TESTS
# ==========================================

# ==========================================
# START WEBSITE
# ==========================================

start_server(State())
