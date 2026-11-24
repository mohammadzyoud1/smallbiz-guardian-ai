import re

# Match numeric values, including negative numbers, commas, and decimals
NUMBER = re.compile(r"-?\d[\d,]*\.?\d*")


# Identify common numbers that should be ignored during validation,  such as week numbers, quantities, and scenario counts
SKIP = re.compile(
    r"\b\d+\s*-?\s*weeks?\b|\bweeks?\s+\d+\b|\b\d+\s*k\b|\b\d+\s+(?:practical\s+)?(?:options|scenarios|flags)\b",
    re.IGNORECASE,
)

# Collect Numeric Values from Tool Outputs
def collect_values(data, out=None):

    # Initialize the output list if this is the first call
    

    out = [] if out is None else out
    # If the data is a dictionary, recursively inspect its values
    if isinstance(data, dict):
        for value in data.values():
            collect_values(value, out)

    # If the data is a list or tuple, inspect each element

    elif isinstance(data, (list, tuple)):
        for value in data:
            collect_values(value, out)


    # Collect numeric values while excluding Boolean values

    elif isinstance(data, (int, float)) and not isinstance(data, bool):
        out.append(float(data))
    return out

# Validate Answer Faithfulness

def check_answer(answer, tool_outputs, tolerance=1.0):

    # Extract all numeric values provided by the tools
    allowed = collect_values(tool_outputs)

    # Store numbers in the answer that cannot be supported by tool outputs

    unsupported = []

    # Extract numeric values mentioned in the AI-generated answer

    for number in numbers_in(answer):

        # Check whether the number matches a tool value within the tolerance

        if not any(
            abs(abs(number) - abs(value)) <= tolerance or abs(abs(number) - abs(value) * 100) <= tolerance
            for value in allowed
        ):      

            # Record numbers that do not match any available tool value
            
            unsupported.append(number)

    # Return the validation result and any unsupported numbers
            
    return {"faithful": not unsupported, "unsupported_numbers": unsupported}


# Extract Numbers from Text
def numbers_in(text):

    # Normalize different Unicode dash characters into standard hyphens

    text = text.replace("–", "-").replace("−", "-").replace("—", "-").replace("‑", "-")

    # Normalize spaces between negative signs and currency symbols

    text = re.sub(r"-\s*\$", "-", text)

    # Remove number patterns that should not be included in validation

    text = SKIP.sub(" ", text)

    # Store the extracted numeric values

    found = []

# Find all numbers matching the configured regular expression
    for match in NUMBER.findall(text):

# Remove thousands separators and trailing decimal points        
        cleaned = match.replace(",", "").rstrip(".")

        # Ignore empty values and convert valid numbers to floats
        if cleaned and cleaned != "-":
            try:
                found.append(float(cleaned))
            except ValueError:
                pass
    return found