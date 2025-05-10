from utils.common import normalize_text, NAME_PATTERN, APPLICATION_NO_PATTERN, DATE_PATTERN
import re

def validate(form_data: dict, extracted_entities: dict, extracted_text: str) -> dict:
    """Validate Income Certificate document."""
    required_fields = ["name", "father_name", "application_no", "date"]
    validation_result = {field: {"form_value": form_data[field], "extracted_value": None, "is_valid": False, "error": None} for field in required_fields}

    extracted_text_upper = extracted_text.upper()

    # Name
    name_labels = ["NAME:", "APPLICANT NAME:"]
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
    father_labels = ["FATHER'S NAME:", "FATHER NAME:"]
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

    # Application Number
    app_no_labels = ["APPLICATION NO:", "CERTIFICATE NO:"]
    for label in app_no_labels:
        label_index = extracted_text_upper.find(label.upper())
        if label_index != -1:
            text_after_label = extracted_text[label_index + len(label):]
            lines = text_after_label.split("\n")
            for line in lines:
                line = line.strip()
                if re.match(APPLICATION_NO_PATTERN, line):
                    validation_result["application_no"]["extracted_value"] = line
                    validation_result["application_no"]["is_valid"] = (form_data["application_no"] == line)
                    if not validation_result["application_no"]["is_valid"]:
                        validation_result["application_no"]["error"] = "Application Number does not match the extracted value."
                    break
            break
    if not validation_result["application_no"]["extracted_value"]:
        app_no_candidates = [item for item in extracted_entities["alphanumeric"] if re.match(APPLICATION_NO_PATTERN, item)]
        if app_no_candidates:
            validation_result["application_no"]["extracted_value"] = app_no_candidates[0]
            validation_result["application_no"]["is_valid"] = (form_data["application_no"] == app_no_candidates[0])
            if not validation_result["application_no"]["is_valid"]:
                validation_result["application_no"]["error"] = "Application Number does not match the extracted value."
        else:
            validation_result["application_no"]["error"] = "Application Number not found in extracted data."

    # Date
    date_labels = ["DATE:", "ISSUE DATE:"]
    for label in date_labels:
        label_index = extracted_text_upper.find(label.upper())
        if label_index != -1:
            text_after_label = extracted_text[label_index + len(label):]
            lines = text_after_label.split("\n")
            for line in lines:
                line = line.strip()
                if re.match(DATE_PATTERN, line):
                    validation_result["date"]["extracted_value"] = line
                    validation_result["date"]["is_valid"] = (form_data["date"] == line)
                    if not validation_result["date"]["is_valid"]:
                        validation_result["date"]["error"] = "Date does not match the extracted value."
                    break
            break
    if not validation_result["date"]["extracted_value"]:
        date_candidates = [item for item in extracted_entities["dates"] if re.match(DATE_PATTERN, item)]
        if date_candidates:
            validation_result["date"]["extracted_value"] = date_candidates[0]
            validation_result["date"]["is_valid"] = (form_data["date"] == date_candidates[0])
            if not validation_result["date"]["is_valid"]:
                validation_result["date"]["error"] = "Date does not match the extracted value."
        else:
            validation_result["date"]["error"] = "Date not found in extracted data."

    return validation_result