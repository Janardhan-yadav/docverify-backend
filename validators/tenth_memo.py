from utils.common import normalize_text, NAME_PATTERN, ROLL_NO_PATTERN, NUMBER_PATTERN
import re

def validate(form_data: dict, extracted_entities: dict, extracted_text: str) -> dict:
    """Validate Tenth Memo document."""
    required_fields = ["name", "father_name", "roll_no", "school_name", "gpa"]
    validation_result = {field: {"form_value": form_data[field], "extracted_value": None, "is_valid": False, "error": None} for field in required_fields}

    # Name
    name_labels = ["CERTIFIED THAT", "Name", "Student Name"]
    extracted_text_upper = extracted_text.upper()
    for label in name_labels:
        label_index = extracted_text_upper.find(label.upper())
        if label_index != -1:
            text_after_label = extracted_text[label_index + len(label):]
            lines = text_after_label.split("\n")
            for line in lines:
                line = line.strip()
                if re.match(NAME_PATTERN, line):
                    validation_result["name"]["extracted_value"] = line
                    form_name = normalize_text(form_data["name"])
                    if form_name == line or " ".join(form_name.split()[:-1]) == line:
                        validation_result["name"]["is_valid"] = True
                    else:
                        validation_result["name"]["error"] = "Name does not match the extracted value."
                    break
            break
    if not validation_result["name"]["extracted_value"]:
        validation_result["name"]["error"] = "Name not found in extracted data."

    # Father's Name
    father_labels = ["FATHER'S NAME", "Father Name"]
    for label in father_labels:
        label_index = extracted_text_upper.find(label.upper())
        if label_index != -1:
            text_after_label = extracted_text[label_index + len(label):]
            lines = text_after_label.split("\n")
            for line in lines:
                line = line.strip()
                if re.match(NAME_PATTERN, line):
                    validation_result["father_name"]["extracted_value"] = line
                    form_father_name = normalize_text(form_data["father_name"])
                    if form_father_name == line or " ".join(form_father_name.split()[:-1]) == line:
                        validation_result["father_name"]["is_valid"] = True
                    else:
                        validation_result["father_name"]["error"] = "Father's Name does not match the extracted value."
                    break
            break
    if not validation_result["father_name"]["extracted_value"]:
        validation_result["father_name"]["error"] = "Father's Name not found in extracted data."

    # Roll Number
    roll_no_labels = ["ROLL NO.", "Roll No", "Roll Number"]
    for label in roll_no_labels:
        label_index = extracted_text_upper.find(label.upper())
        if label_index != -1:
            text_after_label = extracted_text[label_index + len(label):]
            lines = text_after_label.split("\n")
            for line in lines:
                line = line.strip()
                cleaned_line = re.sub(r"[^A-Z0-9]", "", line)  # Remove special characters
                if re.match(ROLL_NO_PATTERN, cleaned_line):
                    validation_result["roll_no"]["extracted_value"] = cleaned_line
                    validation_result["roll_no"]["is_valid"] = (form_data["roll_no"] == cleaned_line)
                    if not validation_result["roll_no"]["is_valid"]:
                        validation_result["roll_no"]["error"] = "Roll Number does not match the extracted value."
                    break
            break
    if not validation_result["roll_no"]["extracted_value"]:
        roll_no_candidates = [item for item in extracted_entities["alphanumeric"] if re.match(ROLL_NO_PATTERN, item)]
        if roll_no_candidates:
            validation_result["roll_no"]["extracted_value"] = roll_no_candidates[0]
            validation_result["roll_no"]["is_valid"] = (form_data["roll_no"] == roll_no_candidates[0])
            if not validation_result["roll_no"]["is_valid"]:
                validation_result["roll_no"]["error"] = "Roll Number does not match the extracted value."
        else:
            validation_result["roll_no"]["error"] = "Roll Number not found in extracted data."

    # School Name
    school_labels = ["SCHOOL", "School", "School Name"]
    for label in school_labels:
        label_index = extracted_text_upper.find(label.upper())
        if label_index != -1:
            text_after_label = extracted_text[label_index + len(label):]
            lines = text_after_label.split("\n")
            for line in lines:
                line = line.strip()
                if re.match(r"[A-Z ]+", line):
                    validation_result["school_name"]["extracted_value"] = line
                    form_school_name = normalize_text(form_data["school_name"])
                    if form_school_name == line or line in form_school_name or form_school_name in line:
                        validation_result["school_name"]["is_valid"] = True
                    else:
                        validation_result["school_name"]["error"] = "School Name does not match the extracted value."
                    break
            break
    if not validation_result["school_name"]["extracted_value"]:
        validation_result["school_name"]["error"] = "School Name not found in extracted data."

    # GPA
    gpa_labels = ["Cumulative Grade Point Average (CGPA)", "CGPA", "GPA"]
    for label in gpa_labels:
        label_index = extracted_text_upper.find(label.upper())
        if label_index != -1:
            text_after_label = extracted_text[label_index + len(label):]
            lines = text_after_label.split("\n")
            for line in lines:
                line = line.strip()
                if re.match(NUMBER_PATTERN, line):
                    validation_result["gpa"]["extracted_value"] = line
                    form_gpa = str(form_data["gpa"])
                    validation_result["gpa"]["is_valid"] = (form_gpa == line or form_gpa == line.rstrip(".0"))
                    if not validation_result["gpa"]["is_valid"]:
                        validation_result["gpa"]["error"] = "GPA does not match the extracted value."
                    break
            break
    if not validation_result["gpa"]["extracted_value"]:
        validation_result["gpa"]["error"] = "GPA not found in extracted data."

    return validation_result