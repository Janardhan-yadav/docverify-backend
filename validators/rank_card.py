from utils.common import normalize_text, NAME_PATTERN, HALL_TICKET_PATTERN, CATEGORY_PATTERN, NUMBER_PATTERN
import re

def validate(form_data: dict, extracted_entities: dict, extracted_text: str) -> dict:
    """Validate Rank Card document."""
    required_fields = ["name", "father_name", "hall_ticket_no", "category", "total_marks", "rank"]
    validation_result = {field: {"form_value": form_data[field], "extracted_value": None, "is_valid": False, "error": None} for field in required_fields}

    extracted_text_upper = extracted_text.upper()

    # Name
    name_labels = ["NAME:", "CANDIDATE NAME:"]
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

    # Hall Ticket Number
    hall_ticket_labels = ["HALL TICKET NO:", "HALL TICKET NUMBER:"]
    for label in hall_ticket_labels:
        label_index = extracted_text_upper.find(label.upper())
        if label_index != -1:
            text_after_label = extracted_text[label_index + len(label):]
            lines = text_after_label.split("\n")
            for line in lines:
                line = line.strip()
                if re.match(HALL_TICKET_PATTERN, line):
                    validation_result["hall_ticket_no"]["extracted_value"] = line
                    validation_result["hall_ticket_no"]["is_valid"] = (form_data["hall_ticket_no"] == line)
                    if not validation_result["hall_ticket_no"]["is_valid"]:
                        validation_result["hall_ticket_no"]["error"] = "Hall Ticket Number does not match the extracted value."
                    break
            break
    if not validation_result["hall_ticket_no"]["extracted_value"]:
        hall_ticket_candidates = [item for item in extracted_entities["alphanumeric"] if re.match(HALL_TICKET_PATTERN, item)]
        if hall_ticket_candidates:
            validation_result["hall_ticket_no"]["extracted_value"] = hall_ticket_candidates[0]
            validation_result["hall_ticket_no"]["is_valid"] = (form_data["hall_ticket_no"] == hall_ticket_candidates[0])
            if not validation_result["hall_ticket_no"]["is_valid"]:
                validation_result["hall_ticket_no"]["error"] = "Hall Ticket Number does not match the extracted value."
        else:
            validation_result["hall_ticket_no"]["error"] = "Hall Ticket Number not found in extracted data."

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

    # Total Marks
    total_marks_labels = ["TOTAL MARKS:", "MARKS:"]
    for label in total_marks_labels:
        label_index = extracted_text_upper.find(label.upper())
        if label_index != -1:
            text_after_label = extracted_text[label_index + len(label):]
            lines = text_after_label.split("\n")
            for line in lines:
                line = line.strip()
                if re.match(NUMBER_PATTERN, line):
                    validation_result["total_marks"]["extracted_value"] = line
                    validation_result["total_marks"]["is_valid"] = (form_data["total_marks"] == line)
                    if not validation_result["total_marks"]["is_valid"]:
                        validation_result["total_marks"]["error"] = "Total Marks does not match the extracted value."
                    break
            break
    if not validation_result["total_marks"]["extracted_value"]:
        validation_result["total_marks"]["error"] = "Total Marks not found in extracted data."

    # Rank
    rank_labels = ["RANK:"]
    for label in rank_labels:
        label_index = extracted_text_upper.find(label.upper())
        if label_index != -1:
            text_after_label = extracted_text[label_index + len(label):]
            lines = text_after_label.split("\n")
            for line in lines:
                line = line.strip()
                if re.match(r"\d+", line):
                    validation_result["rank"]["extracted_value"] = line
                    validation_result["rank"]["is_valid"] = (form_data["rank"] == line)
                    if not validation_result["rank"]["is_valid"]:
                        validation_result["rank"]["error"] = "Rank does not match the extracted value."
                    break
            break
    if not validation_result["rank"]["extracted_value"]:
        validation_result["rank"]["error"] = "Rank not found in extracted data."

    return validation_result