# This file will contain the logic for data preparation for the NER and Validation models.
# It will include functions to generate synthetic data, add OCR-like noise, and annotate data.

import random
import string

# Document Types and Key Fields:
DOC_TYPES_FIELDS = {
    "hall_ticket": ["student_name", "roll_number", "exam_date", "exam_center"],
    "rank_card": ["candidate_name", "rank", "score", "exam_name"],
    "allotment_order": ["candidate_name", "allotted_college", "course", "allotment_date"],
    "income_certificate": ["applicant_name", "father_name", "annual_income", "certificate_number"],
    "caste_certificate": ["applicant_name", "caste_category", "certificate_number", "issuing_authority"],
    "tenth_memo": ["student_name", "father_name", "roll_number", "school_name", "gpa"]
}

# Templates for each document type
TEMPLATES = {
    "tenth_memo": [
        "BOARD OF SECONDARY EDUCATION TELANGANA STATE, INDIA TS-GG16338 SECONDARY SCHOOL CERTIFICATE REGULAR PC/06/15039/0063523/5 CERTIFIED THAT {student_name} FATHER'S NAME {father_name} ROLL NO. {roll_number} SCHOOL {school_name} SSC Cumulative Grade Point Average (CGPA) {gpa} DATE OF ISSUE 21/05/2021",
        "GOVERNMENT OF ANDHRA PRADESH, BOARD OF SECONDARY EDUCATION, AMARAVATI. SSC MEMORANDUM. NAME: {student_name}, FATHER: {father_name}, ROLL NUMBER: {roll_number}, SCHOOL: {school_name}, CGPA: {gpa}. DATE: 15/06/2022."
    ],
    "hall_ticket": [
        "EXAMINATION HALL TICKET. University of Excellence. Name: {student_name}, Roll No: {roll_number}, Exam Date: {exam_date}, Center: {exam_center}. Instructions: Reach 30 mins prior.",
        "National Testing Agency. Admit Card. Candidate: {student_name}, Roll: {roll_number}. Date of Exam: {exam_date}. Venue: {exam_center}."
    ],
    "rank_card": [
        "NATIONAL ELIGIBILITY CUM ENTRANCE TEST (NEET). SCORE CARD. Name: {candidate_name}, Rank: {rank}, Score: {score}, Exam: {exam_name}. Date: 10/10/2023.",
        "JOINT ENTRANCE EXAMINATION (JEE) ADVANCED. RANK CARD. Candidate: {candidate_name}, All India Rank: {rank}, Marks Obtained: {score}, Examination: {exam_name}."
    ],
    "allotment_order": [
        "PROVISIONAL ALLOTMENT ORDER. Name: {candidate_name}, College: {allotted_college}, Course: {course}, Allotment Date: {allotment_date}. Director of Admissions.",
        "SEAT ALLOTMENT LETTER. Candidate Name: {candidate_name}, Allotted Institute: {allotted_college}, Program: {course}, Date of Allotment: {allotment_date}."
    ],
    "income_certificate": [
        "INCOME CERTIFICATE. This is to certify that {applicant_name}, son/daughter of {father_name}, has an annual income of Rs. {annual_income}. Certificate No: {certificate_number}. Tahsildar Office.",
        "GOVERNMENT OF XYZ. REVENUE DEPARTMENT. ANNUAL INCOME CERTIFICATE. Applicant: {applicant_name}, S/O, D/O: {father_name}, Annual Family Income: {annual_income}. Cert. ID: {certificate_number}."
    ],
    "caste_certificate": [
        "CASTE CERTIFICATE. Certified that {applicant_name} belongs to the {caste_category} caste. Certificate No: {certificate_number}. Issuing Authority: {issuing_authority}. MRO Office.",
        "COMMUNITY CERTIFICATE. Name: {applicant_name}, Community: {caste_category}. Certificate ID: {certificate_number}. Issued by: {issuing_authority}."
    ]
}

# Placeholder data for generating synthetic examples
PLACEHOLDER_DATA = {
    "student_name": ["John Doe", "Alice Smith", "Bob Johnson", "Priya Sharma", "Amit Patel"],
    "father_name": ["Peter Doe", "James Smith", "Robert Johnson", "Rajesh Sharma", "Suresh Patel"],
    "roll_number": ["1234567890", "0987654321", "A1B2C3D4E5", "R210012345", "S190054321"],
    "school_name": ["ZP High School Madhapur", "Global International School", "St. Ann's High School", "Kendriya Vidyalaya", "Delhi Public School"],
    "gpa": ["9.5", "8.7", "10.0", "7.2", "9.1"],
    "exam_date": ["15/03/2024", "20-04-2024", "05 May 2024", "10.06.2024", "July 1st, 2024"],
    "exam_center": ["City College Main Building", "Online Test Center A", "Govt. Degree College Auditorium", "Tech Park Exam Hall", "Rural School Campus"],
    "candidate_name": ["Emily White", "Michael Brown", "Sophia Green", "David Lee", "Olivia Wilson"],
    "rank": ["120", "543", "23", "1050", "88"],
    "score": ["650/720", "98.5 percentile", "320/360", "180/200", "75%"],
    "exam_name": ["NEET UG 2023", "JEE Advanced 2024", "CAT 2023", "GATE CS 2024", "UPSC Prelims 2023"],
    "allotted_college": ["IIT Bombay", "AIIMS Delhi", "NIT Warangal", "IIM Ahmedabad", "JNTU Hyderabad"],
    "course": ["Computer Science Engineering", "MBBS", "Electrical Engineering", "MBA", "Civil Engineering"],
    "allotment_date": ["25/07/2023", "10-08-2023", "15 Sep 2023", "01.10.2023", "November 5th, 2023"],
    "applicant_name": ["Ramesh Kumar", "Sita Devi", "Arjun Singh", "Lakshmi Reddy", "Fatima Begum"],
    "annual_income": ["1,50,000", "3,00,000", "80,000", "5,50,000", "2,25,000"],
    "certificate_number": ["INC12345XYZ", "REV09876ABC", "TAH54321PQR", "MRO67890LMN", "GOV23456DEF"],
    "caste_category": ["Scheduled Caste (SC)", "Other Backward Class (OBC)", "Scheduled Tribe (ST)", "General", "Economically Weaker Section (EWS)"],
    "issuing_authority": ["Tahsildar, Mandal Office", "Revenue Divisional Officer", "District Collector", "MRO, XYZ Division", "Sub-Collector Office"]
}

def add_ocr_noise(text, noise_level=0.05):
    noisy_text = list(text)
    num_chars_to_change = int(len(text) * noise_level)
    for _ in range(num_chars_to_change):
        idx = random.randint(0, len(text) - 1)
        if noisy_text[idx].isspace():
            continue
        # Randomly substitute, insert, or delete
        action = random.choice(["substitute", "insert", "delete", "case"])
        if action == "substitute" and noisy_text[idx].isalnum():
            noisy_text[idx] = random.choice(string.ascii_letters + string.digits)
        elif action == "insert":
            noisy_text.insert(idx, random.choice(string.ascii_letters + string.digits + " "))
        elif action == "delete" and len(noisy_text) > 1:
            noisy_text.pop(idx)
        elif action == "case":
            if noisy_text[idx].islower():
                noisy_text[idx] = noisy_text[idx].upper()
            elif noisy_text[idx].isupper():
                noisy_text[idx] = noisy_text[idx].lower()
    return "".join(noisy_text)

def generate_synthetic_data(doc_type, num_examples=500):
    synthetic_examples = []
    if doc_type not in TEMPLATES or doc_type not in DOC_TYPES_FIELDS:
        print(f"Templates or fields not defined for document type: {doc_type}")
        return []

    templates = TEMPLATES[doc_type]
    fields = DOC_TYPES_FIELDS[doc_type]

    for i in range(num_examples):
        template = random.choice(templates)
        data_instance = {}
        filled_template = template
        annotations = {"entities": []} # For NER

        for field in fields:
            field_value = random.choice(PLACEHOLDER_DATA.get(field, [f"<{field}_placeholder>"]))
            data_instance[field] = field_value
            
            # Basic NER annotation - find start and end of placeholder
            # A more robust method would be needed for real data or complex templates
            placeholder_tag = "{" + field + "}"
            start_index = filled_template.find(placeholder_tag)
            if start_index != -1:
                end_index = start_index + len(placeholder_tag)
                # Replace placeholder with actual value for the final text
                filled_template = filled_template.replace(placeholder_tag, field_value, 1)
                # Adjust end_index for the actual value length
                # This is a simplified annotation; real NER needs token-level BIO tagging
                # For now, we'll store the value and its intended field for later, more precise annotation
                # or for creating validation pairs.
                # annotations["entities"].append((start_index, start_index + len(field_value), field.upper()))
            else:
                # If placeholder not in template, it might be a compound field or different format
                # This part needs more sophisticated handling for robust annotation
                pass 
        
        # Add OCR noise to the final text
        noisy_text = add_ocr_noise(filled_template)
        
        # For NER, we need to re-align annotations after noise or use a more robust annotation strategy.
        # For now, we'll focus on generating text and field pairs for validation model training.
        # The NER model training would require more careful annotation of the noisy_text.
        
        # Store the noisy text and the original clean data for validation model training
        # and for later, more detailed NER annotation if needed.
        synthetic_examples.append({
            "text": noisy_text,
            "form_data": data_instance, # Clean data used to fill template
            "doc_type": doc_type
            # "ner_annotations_raw": annotations # Raw annotations before noise, needs re-alignment
        })
    return synthetic_examples

# Example usage:
# tenth_memo_data = generate_synthetic_data("tenth_memo", 10)
# for example in tenth_memo_data:
#     print("Text:", example["text"])
#     print("Form Data:", example["form_data"])
#     print("---")

# TODO:
# 1. Refine NER annotation to be robust to OCR noise (e.g., character-level or token-level BIO tagging on noisy text).
# 2. Generate data for all document types.
# 3. Save generated data in a format suitable for training (e.g., JSONL, CSV).
# 4. Create specific data for the validation model (pairs of extracted vs form fields with match/no-match labels).

pass

