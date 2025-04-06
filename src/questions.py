"""
Question definition module for the Data Flow Assessment tool.
This module contains the structure of all questions, their types, and branching logic.
"""

# Define question types
TEXT = "text"
SINGLE_CHOICE = "single_choice"
MULTIPLE_CHOICE = "multiple_choice"
NUMBER = "number"

# Define the questionnaire structure
questions = [
    {
        "id": "system_name",
        "type": TEXT,
        "text": "What is the name of the system you're analyzing?",
        "required": True,
        "help": "Enter the name of the data processing system or application"
    },
    {
        "id": "system_description",
        "type": TEXT,
        "text": "Briefly describe the purpose of this system:",
        "required": True,
        "multiline": True,
        "help": "What does this system do? What is its primary function?"
    },
    {
        "id": "data_parties",
        "type": TEXT,
        "text": "List all parties involved in the data flow (comma separated):",
        "required": True,
        "store_as_list": True,
        "help": "Include all organizations, individuals, or entities that interact with the data"
    },
    {
        "id": "party_details",
        "type": "repeated_section",
        "repeat_for": "data_parties",
        "questions": [
            {
                "id": "party_role_{item}",
                "type": SINGLE_CHOICE,
                "text": "What role does {item} play in the data flow?",
                "options": ["Data Controller", "Data Processor", "Joint Controller", "Data Subject", "Third Party Recipient"],
                "required": True,
                "help": "The role determines responsibilities under data protection regulations"
            },
            {
                "id": "party_location_{item}",
                "type": TEXT,
                "text": "Where is {item} located (country/region)?",
                "required": True
            },
            {
                "id": "party_process_{item}",
                "type": TEXT,
                "text": "What processing activities does {item} perform?",
                "required": True,
                "multiline": True,
                "condition": {
                    "question_id": "party_role_{item}",
                    "operator": "in",
                    "value": ["Data Controller", "Data Processor", "Joint Controller"]
                }
            }
        ]
    },
    {
        "id": "data_categories",
        "type": MULTIPLE_CHOICE,
        "text": "What categories of data are processed in this system?",
        "options": [
            "Personal Identifiers", 
            "Contact Information", 
            "Financial Data", 
            "Health Data",
            "Biometric Data",
            "Location Data",
            "Online Identifiers",
            "Behavioral Data",
            "Demographic Data",
            "Professional Data",
            "Other"
        ],
        "required": True,
        "help": "Select all categories that apply to your system"
    },
    {
        "id": "other_data_categories",
        "type": TEXT,
        "text": "Please specify other data categories:",
        "required": True,
        "condition": {
            "question_id": "data_categories",
            "operator": "contains",
            "value": "Other"
        }
    },
    {
        "id": "data_attributes",
        "type": TEXT,
        "text": "List all specific data attributes that flow through the system (comma separated):",
        "required": True,
        "store_as_list": True,
        "help": "E.g., name, email, address, phone number, purchase history, etc."
    },
    {
        "id": "attribute_details",
        "type": "repeated_section",
        "repeat_for": "data_attributes",
        "questions": [
            {
                "id": "attribute_type_{item}",
                "type": SINGLE_CHOICE,
                "text": "What type of data is {item}?",
                "options": ["Personal Data", "Special Category (Sensitive) Personal Data", "Non-Personal Data"],
                "required": True,
                "help": "Special categories include race, ethnicity, political opinions, religious beliefs, health data, etc."
            },
            {
                "id": "attribute_purpose_{item}",
                "type": TEXT,
                "text": "What is the purpose of collecting {item}?",
                "required": True,
                "condition": {
                    "question_id": "attribute_type_{item}",
                    "operator": "in",
                    "value": ["Personal Data", "Special Category (Sensitive) Personal Data"]
                }
            },
            {
                "id": "attribute_legal_basis_{item}",
                "type": SINGLE_CHOICE,
                "text": "What is the legal basis for processing {item}?",
                "options": [
                    "Consent", 
                    "Contract Performance", 
                    "Legal Obligation", 
                    "Vital Interests", 
                    "Public Interest", 
                    "Legitimate Interests"
                ],
                "required": True,
                "condition": {
                    "question_id": "attribute_type_{item}",
                    "operator": "in",
                    "value": ["Personal Data", "Special Category (Sensitive) Personal Data"]
                }
            }
        ]
    },
    {
        "id": "processing_activities",
        "type": MULTIPLE_CHOICE,
        "text": "What processing activities are performed on the data?",
        "options": [
            "Collection", 
            "Recording", 
            "Organization", 
            "Structuring", 
            "Storage",
            "Adaptation/Alteration",
            "Retrieval",
            "Consultation",
            "Use",
            "Disclosure",
            "Dissemination",
            "Alignment/Combination",
            "Restriction",
            "Erasure/Destruction",
            "Profiling/Automated Decision-Making",
            "Other"
        ],
        "required": True
    },
    {
        "id": "data_flows",
        "type": TEXT,
        "text": "Describe the main data flows between parties (who sends what to whom):",
        "required": True,
        "multiline": True,
        "help": "E.g., 'Company A sends customer names and emails to Vendor B for marketing purposes'"
    },
    {
        "id": "data_transfers",
        "type": SINGLE_CHOICE,
        "text": "Are there any cross-border data transfers?",
        "options": ["Yes", "No"],
        "required": True
    },
    {
        "id": "transfer_details",
        "type": "section",
        "condition": {
            "question_id": "data_transfers",
            "operator": "==",
            "value": "Yes"
        },
        "questions": [
            {
                "id": "transfer_countries",
                "type": TEXT,
                "text": "List all countries involved in cross-border transfers (comma separated):",
                "required": True,
                "store_as_list": True
            },
            {
                "id": "transfer_safeguards",
                "type": MULTIPLE_CHOICE,
                "text": "What safeguards are in place for these transfers?",
                "options": [
                    "Standard Contractual Clauses", 
                    "Binding Corporate Rules", 
                    "Adequacy Decision", 
                    "Explicit Consent", 
                    "Derogations for Specific Situations",
                    "None"
                ],
                "required": True
            }
        ]
    },
    {
        "id": "retention_period",
        "type": TEXT,
        "text": "What is the data retention period?",
        "required": True,
        "help": "How long is the data kept before being deleted or anonymized?"
    },
    {
        "id": "security_measures",
        "type": MULTIPLE_CHOICE,
        "text": "What security measures are implemented?",
        "options": [
            "Encryption", 
            "Access Controls", 
            "Regular Audits", 
            "Data Minimization", 
            "Anonymization/Pseudonymization",
            "Backup and Recovery",
            "Incident Response Plan",
            "Staff Training",
            "Other"
        ],
        "required": True
    },
    {
        "id": "security_other",
        "type": TEXT,
        "text": "Please specify other security measures:",
        "required": True,
        "condition": {
            "question_id": "security_measures",
            "operator": "contains",
            "value": "Other"
        }
    }
]

def get_question_by_id(question_id):
    """
    Find a question by its ID in the questions list.
    
    Args:
        question_id (str): The ID of the question to find
        
    Returns:
        dict or None: The question with the matching ID, or None if not found
    """
    for question in questions:
        if question["id"] == question_id:
            return question
        
        # Check for nested questions in sections
        if question["type"] in ["section", "repeated_section"] and "questions" in question:
            for nested_question in question["questions"]:
                # For repeated sections, the ID may contain {item} placeholder
                if nested_question["id"] == question_id or nested_question["id"].split("_{")[0] == question_id.split("_")[0]:
                    return nested_question
    
    return None
