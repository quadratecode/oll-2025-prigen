"""
Question definition module for the Data Flow Assessment tool.
This module contains the structure of all questions, their types, and branching logic.
"""

# Define question types
TEXT = "text"
SINGLE_CHOICE = "single_choice"
MULTIPLE_CHOICE = "multiple_choice"
NUMBER = "number"
SPECIAL = "special"  # For questions that need special handling
TOGGLE = "toggle"  # For yes/no questions

# Define sensitive data categories for question 5.1
SENSITIVE_DATA_CATEGORIES = [
    "Daten über religiöse, weltanschauliche, politische oder gewerkschaftliche Ansichten oder Tätigkeiten (natürliche Personen)",
    "Daten über die Gesundheit, die Intimsphäre oder die Zugehörigkeit zu einer Rasse oder Ethnie (natürliche Personen)",
    "genetische Daten (natürliche Personen)",
    "biometrische Daten, die eine natürliche Person eindeutig identifizieren (natürliche Personen)",
    "Daten über verwaltungs- und strafrechtliche Verfolgungen oder Sanktionen (natürliche Personen)",
    "Daten über Massnahmen der sozialen Hilfe (natürliche Personen)",
    "Daten über verwaltungs- und strafrechtliche Verfolgungen und Sanktionen (juristische Personen)",
    "Daten über Berufs-, Geschäfts- und Fabrikationsgeheimnisse (juristische Personen)",
]

SYSTEM_DEFAULT = [
    "IT Server 1",
    "Elektronische Patientenakte",
    "Laborinformationssystem",
    "Radiologie-PACS",
    "Apothekenmanagementsystem",
    "Krankenhausinformationssystem",
    "Abrechnungssystem",
    "Personalverwaltungssystem",
    "Terminplanungssystem",
    "Lagerverwaltungssystem",
]
VERANTWORTLICH_DEFAULT = [
    "Hans Müller",
    "Ursula Weber",
    "Marco Bernasconi",
    "Sophie Dubois",
    "Peter Keller",
    "Marie Zürcher",
    "Thomas Schmid",
    "Heidi Brunner",
    "Daniel Meier",
    "Anna Steiner",
]
BEARBEITER_DEFAULT = [
    "Dr. Petra Koch",
    "Dr. Stefan Wagner",
    "Dr. Lisa Huber",
    "Pfleger Martin Baumann",
    "Schwester Andrea Moser",
    "Dr. Michael Fischer",
    "Dr. Sarah Berg",
    "Pfleger David Schmitz",
    "Schwester Julia Keller",
    "Dr. Thomas Weber",
    "Dr. Christina Müller",
    "Pfleger Simon Bauer",
    "Schwester Nicole Meyer",
    "Dr. Andreas Hoffmann",
    "Dr. Sandra Wolf",
    "Chirurgische Abteilung",
    "Innere Medizin",
    "Radiologie",
    "Notfallstation",
    "Kardiologie",
    "Pädiatrie",
    "Onkologie",
    "Gynäkologie",
    "Intensivstation",
    "Pflegeabteilung",
    "Pathologie",
    "Anästhesiologie",
    "Dermatologie",
    "Psychiatrie",
    "Ambulanz",
]

SYSTEM_ZIELE_DEFAULT = [
    "zur Verbesserung des Workflows",
    "zum Speichern von Patientendaten",
    "zur Dokumentation von Behandlungen",
    "zum Management der Ressourcen",
    "zur Abrechnung von Leistungen",
    "zur Qualitätssicherung",
    "zum Austausch von Informationen",
    "zur Planung von Terminen",
    "zum Controlling der Prozesse",
    "zur Integration verschiedener Systeme",
]
BEARBEITUNGS_ZWECK_DEFAULT = [
    "zum Vertragsabschluss oder -abwicklung",
    "zur Prüfung der Kreditwürdigkeit",
    "zum Wettbewerb",
    "zur Erfüllung gesetzlicher Grundlagen",
    "zur Erfüllung eines überwiegenden öffentlichen Interesses",
    "zur Erfüllung eines überwiegenden privaten Interesses",
    "zur Einwilligung der betroffenen Person",
]
DATENARTEN_DEFAULT = [
    "Patientenstammdaten",
    "Spenderdaten",
    "Laborergebnisse",
    "Medizinische Befunde",
    "Behandlungshistorie",
    "Medikamentendaten",
    "Versicherungsinformationen",
    "Impfdaten",
    "Allergien und Unverträglichkeiten",
    "Familienanamnese",
    "Bildgebende Diagnostik",
    "Therapiepläne",
    "Überweisungsdaten",
    "Notfalldaten",
    "Pflegedokumentation",
]


# Define the questionnaire structure
questions = [
    # Question 1: Systems used
    {
        "id": "systems",
        "type": TEXT,
        "text": "Welche Systeme werden eingesetzt?",
        "required": True,
        "store_as_list": True,
        "default": SYSTEM_DEFAULT,
        # Denkfehler hier : der User kann mehrere Systeme pro Eintrag eingeben.
        # old        "help": "Geben Sie die Namen der eingesetzten Systeme ein, durch Kommas getrennt.",
        "help": "Geben Sie die Namen der eingesetzten Systeme ein. Bitte auf Hinzufügen clicken, damit die Liste aktualisiert wird.",
        "max_length": 500,
    },
    # Question 1.1-1.2: Details for each system
    {
        "id": "system_details",
        "type": "repeated_section",
        "repeat_for": "systems",
        "questions": [
            {
                "id": "system_purpose_{item}",
                "type": TEXT,
                "text": "Wozu dient das System {item}?",
                "default": SYSTEM_ZIELE_DEFAULT,
                "required": True,
                "multiline": True,
                "max_length": 500,
            },
            {
                "id": "system_responsible_{item}",
                "type": TEXT,
                "text": "Wer ist für das System {item} verantwortlich?",
                "default": VERANTWORTLICH_DEFAULT,
                "required": True,
                "store_as_list": True,
                "help": "Geben Sie die Namen der Verantwortlichen ein.",
                "max_length": 500,
            },
        ],
    },
    # Question 2: Are there additional responsible parties? (Toggle question)
    {
        "id": "has_additional_responsible",
        "type": TOGGLE,
        "text": "Gibt es Verantwortliche, die nicht Systembetreiber sind?",
        "required": True,
        "default": False,
    },
    # Question 2.1: Additional responsible parties (only shown if toggle is "Ja")
    {
        "id": "additional_responsible",
        "type": TEXT,
        "text": "Namen der zusätzlichen Verantwortlichen:",
        "default": VERANTWORTLICH_DEFAULT,
        "default": VERANTWORTLICH_DEFAULT,
        "required": True,
        "store_as_list": True,
        "help": "Geben Sie die Namen weiterer Verantwortlicher ein.",
        "max_length": 500,
        "condition": {
            "question_id": "has_additional_responsible",
            "operator": "==",
            "value": True,
        },
    },
    # Question 3: Processors for each responsible party (special handling)
    {
        "id": "responsible_processors",
        "type": SPECIAL,
        "text": "Je Verantwortlicher: Welche Bearbeiter gehören zu diesem Verantwortlichen?",
        "special_type": "responsible_processors",
        "help": "Diese Frage wird für jeden Verantwortlichen wiederholt.",
    },
    # Question 4: Processing purposes
    {
        "id": "processing_purposes",
        "type": TEXT,
        "text": "Welche Bearbeitungszwecke gibt es?",
        "default": BEARBEITUNGS_ZWECK_DEFAULT,
        "required": True,
        "store_as_list": True,
        "help": "Geben Sie die möglichen Bearbeitungszwecke ein getrennt.",
        "max_length": 500,
    },
    # Question 5: Data types
    {
        "id": "data_types",
        "type": TEXT,
        "text": "Welche Datenarten werden im System behandelt?",
        "default": DATENARTEN_DEFAULT,
        "required": True,
        "store_as_list": True,
        "help": "Geben Sie die Datenarten ein",
        "max_length": 500,
    },
    # Question 5.1: Categories for each data type
    {
        "id": "data_type_details",
        "type": "repeated_section",
        "repeat_for": "data_types",
        "questions": [
            {
                "id": "data_categories_{item}",
                "type": MULTIPLE_CHOICE,
                "text": "Welche Datenkategorien sind in der Datenart {item} enthalten?",
                "options": SENSITIVE_DATA_CATEGORIES,
                "required": True,
                "help": "Wählen Sie alle zutreffenden Datenkategorien aus.",
            }
        ],
    },
    # Question 6: Matrix for processors, purposes, and data types (special handling)
    {
        "id": "processor_matrix",
        "type": SPECIAL,
        "text": "Je Bearbeiter: Zu welchem Zweck bearbeitet dieser Bearbeiter welche Datenarten?",
        "special_type": "processor_matrix",
        "help": "Bitte geben Sie für jeden Bearbeiter an, zu welchem Zweck er welche Datenarten bearbeitet.",
        "hide_quick_selection": True,  # Flag to hide quick selection
    },
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
        if question["type"] == "repeated_section" and "questions" in question:
            for nested_question in question["questions"]:
                # For repeated sections, the ID may contain {item} placeholder
                if (
                    nested_question["id"] == question_id
                    or nested_question["id"].split("_{")[0] == question_id.split("_")[0]
                ):
                    return nested_question

    return None


def collect_all_responsible_parties(answers):
    """
    Collect all responsible parties from the answers.

    Args:
        answers (dict): The current answers

    Returns:
        list: List of all responsible parties
    """
    all_responsible = []

    # Collect from system_responsible_{item} questions
    for key, value in answers.items():
        if key.startswith("system_responsible_") and isinstance(value, list):
            all_responsible.extend(value)

    # Add from additional_responsible only if has_additional_responsible is True
    if (
        answers.get("has_additional_responsible", False)
        and "additional_responsible" in answers
        and isinstance(answers["additional_responsible"], list)
    ):
        all_responsible.extend(answers["additional_responsible"])

    # Remove duplicates and return
    return sorted(list(set(all_responsible)))


def collect_all_processors(answers):
    """
    Collect all processors from the answers.

    Args:
        answers (dict): The current answers

    Returns:
        list: List of all processors
    """
    all_processors = []

    # Collect processors from each responsible party
    for key, value in answers.items():
        if key.startswith("processors_") and isinstance(value, list):
            all_processors.extend(value)

    # Remove duplicates and return
    return sorted(list(set(all_processors)))
