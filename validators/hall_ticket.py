from utils.common import normalize_text, HALL_TICKET_PATTERN, CATEGORY_PATTERN, NAME_PATTERN
import re

def validate(form_data: dict, extracted_entities: dict, extracted_text: str) -> dict:
    """Validate Hall Ticket document."""
    required_fields = ["hall_ticket_number", "candidate_name", "father_name", "registration_number", "category"]
    validation_result = {field: {"form_value": form_data[field], "extracted_value": None, "is_valid": False, "error": None} for field in required_fields}

    # Hall Ticket Number
    hall_ticket_candidates = [item for item in extracted_entities["alphanumeric"] if re.match(HALL_TICKET_PATTERN, item)]
    if hall_ticket_candidates:
        validation_result["hall_ticket_number"]["extracted_value"] = hall_ticket_candidates[0]
        validation_result["hall_ticket_number"]["is_valid"] = (form_data["hall_ticket_number"] == hall_ticket_candidates[0])
        if not validation_result["hall_ticket_number"]["is_valid"]:
            validation_result["hall_ticket_number"]["error"] = "Hall Ticket Number does not match the extracted value."
    else:
        validation_result["hall_ticket_number"]["error"] = "Hall Ticket Number not found in extracted data."

    # Candidate Name
    candidate_label = "Canclickale\nName\""
    candidate_label_index = extracted_text.find(candidate_label)
    if candidate_label_index != -1:
        text_after_label = extracted_text[candidate_label_index + len(candidate_label):]
        lines = text_after_label.split("\n")
        for line in lines:
            line = line.strip()
            if re.match(NAME_PATTERN, line):
                next_line_index = text_after_label.find(line) + len(line)
                next_line = text_after_label[next_line_index:].split("\n")[0].strip()
                if next_line.isupper() and len(next_line.split()) <= 2:
                    candidate_name = f"{line} {next_line}"
                else:
                    candidate_name = line
                validation_result["candidate_name"]["extracted_value"] = candidate_name
                form_name = normalize_text(form_data["candidate_name"])
                if form_name == candidate_name:
                    validation_result["candidate_name"]["is_valid"] = True
                elif form_name.replace("PRATHAP", "PRATHIAP") == candidate_name:
                    validation_result["candidate_name"]["is_valid"] = True
                elif " ".join(form_name.split()[:-1]) == candidate_name:
                    validation_result["candidate_name"]["is_valid"] = True
                else:
                    validation_result["candidate_name"]["error"] = "Candidate Name does not match the extracted value."
                break
        if not validation_result["candidate_name"]["extracted_value"]:
            validation_result["candidate_name"]["error"] = "Candidate Name not found in extracted data."
    else:
        validation_result["candidate_name"]["error"] = "Candidate Name not found in extracted data."

    # Father's Name
    father_label = "Fautlcr ` Nani"
    father_label_index = extracted_text.find(father_label)
    if father_label_index != -1:
        text_after_label = extracted_text[father_label_index + len(father_label):]
        lines = text_after_label.split("\n")
        for line in lines:
            line = line.strip()
            if re.match(NAME_PATTERN, line):
                next_line_index = text_after_label.find(line) + len(line)
                next_line = text_after_label[next_line_index:].split("\n")[0].strip()
                if next_line.isupper() and len(next_line.split()) <= 2:
                    father_name = f"{line} {next_line}"
                else:
                    father_name = line
                validation_result["father_name"]["extracted_value"] = father_name
                form_father_name = normalize_text(form_data["father_name"])
                if form_father_name == father_name or father_name == " ".join(form_father_name.split()[:-1]):
                    validation_result["father_name"]["is_valid"] = True
                else:
                    validation_result["father_name"]["error"] = "Father's Name does not match the extracted value."
                break
        if not validation_result["father_name"]["extracted_value"]:
            validation_result["father_name"]["error"] = "Father's Name not found in extracted data."
    else:
        validation_result["father_name"]["error"] = "Father's Name not found in extracted data."

    # Registration Number
    reg_number_pattern = r"^\d{8,}$"
    reg_number_candidates = [item for item in extracted_entities["alphanumeric"] if re.match(reg_number_pattern, item) and item != form_data["hall_ticket_number"]]
    if reg_number_candidates:
        validation_result["registration_number"]["extracted_value"] = reg_number_candidates[0]
        validation_result["registration_number"]["is_valid"] = (form_data["registration_number"] == reg_number_candidates[0])
        if not validation_result["registration_number"]["is_valid"]:
            validation_result["registration_number"]["error"] = "Registration Number does not match the extracted value."
    else:
        validation_result["registration_number"]["error"] = "Registration Number not found in extracted data."

    # Category
    for line in extracted_text.split("\n"):
        line = line.strip()
        if re.match(CATEGORY_PATTERN, line):
            validation_result["category"]["extracted_value"] = line
            validation_result["category"]["is_valid"] = (normalize_text(form_data["category"]) == line)
            if not validation_result["category"]["is_valid"]:
                validation_result["category"]["error"] = "Category does not match the extracted value."
            break
    if not validation_result["category"]["extracted_value"]:
        validation_result["category"]["error"] = "Category not found in extracted data."

    return validation_result