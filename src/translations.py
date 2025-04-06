"""
Translations module for the Data Flow Assessment tool.
This module contains all UI strings to support internationalization.
"""

# Available languages
AVAILABLE_LANGUAGES = ["de", "en"]
DEFAULT_LANGUAGE = "de"

# Translation dictionaries for each language
translations = {
    "de": {
        # App title and navigation
        "app_title": "Datenfluss-Bewertungstool",
        "sidebar_title": "Datenfluss-Bewertung",
        "summary_title": "Zusammenfassung der Antworten",
        "edit_responses": "Antworten bearbeiten",
        "visualize": "Datenflüsse visualisieren",
        "policy_suggestions": "Richtlinienvorschläge",
        # Navigation buttons
        "previous": "⬅️ Zurück",
        "next": "Weiter ➡️",
        "complete": "Abschließen ✅",
        # Session management
        "session_management": "Sitzungsverwaltung",
        "continue_session": "Aktuelle Sitzung fortsetzen",
        "export_session": "Sitzung exportieren",
        "import_session": "Sitzung importieren",
        "new_session": "Neue Sitzung starten",
        "session_name": "Sitzungsname (optional):",
        "download_session": "Sitzungsdatei herunterladen",
        "upload_session": "Gespeicherte Sitzungsdatei hochladen:",
        "import_button": "Sitzung importieren",
        "confirm_new": "Neue Sitzung bestätigen",
        # Messages
        "required_warning": "Diese Frage ist erforderlich, um fortzufahren.",
        "section_required_warning": "Bitte beantworten Sie alle erforderlichen Fragen in diesem Abschnitt, um fortzufahren.",
        "completion_success": "Bewertung abgeschlossen! Vergessen Sie nicht, Ihre Sitzungsdatei herunterzuladen, um Ihre Arbeit zu speichern.",
        "section_not_applicable": "Dieser Abschnitt ist basierend auf Ihren vorherigen Antworten nicht anwendbar.",
        # Question-specific help texts and labels
        "your_answer": "Ihre Antwort:",
        "select_one": "Wählen Sie eine Option:",
        "select_all": "Wählen Sie alle zutreffenden Optionen:",
        # Matrix question
        "processor_matrix_heading": "Bearbeiter, Zweck und Datenarten",
        "processor": "Bearbeiter",
        "purpose": "Zweck",
        "data_type": "Datenart",
        "matrix_select_all": "Alle auswählen",
        "matrix_no_data": "Bitte beantworten Sie zuerst die Fragen zu Bearbeitern, Zwecken und Datenarten.",
    },
    "en": {
        # App title and navigation
        "app_title": "Data Flow Assessment Tool",
        "sidebar_title": "Data Flow Assessment",
        "summary_title": "Summary of Responses",
        "edit_responses": "Edit Responses",
        "visualize": "Visualize Data Flows",
        "policy_suggestions": "Policy Suggestions",
        # Navigation buttons
        "previous": "⬅️ Previous",
        "next": "Next ➡️",
        "complete": "Complete ✅",
        # Session management
        "session_management": "Session Management",
        "continue_session": "Continue Current Session",
        "export_session": "Export Session",
        "import_session": "Import Session",
        "new_session": "Start New Session",
        "session_name": "Session name (optional):",
        "download_session": "Download Session File",
        "upload_session": "Upload a saved session file:",
        "import_button": "Import Session",
        "confirm_new": "Confirm New Session",
        # Messages
        "required_warning": "This question is required to proceed.",
        "section_required_warning": "Please answer all required questions in this section to proceed.",
        "completion_success": "Assessment completed! Don't forget to download your session file to save your work.",
        "section_not_applicable": "This section is not applicable based on your previous answers.",
        # Question-specific help texts and labels
        "your_answer": "Your answer:",
        "select_one": "Select one:",
        "select_all": "Select all that apply:",
        # Matrix question
        "processor_matrix_heading": "Processors, Purposes and Data Types",
        "processor": "Processor",
        "purpose": "Purpose",
        "data_type": "Data Type",
        "matrix_select_all": "Select All",
        "matrix_no_data": "Please answer the questions about processors, purposes, and data types first.",
    },
}


def get_text(key, language=DEFAULT_LANGUAGE):
    """
    Get a translated string for the given key and language.

    Args:
        key (str): The translation key
        language (str, optional): The language code. Defaults to DEFAULT_LANGUAGE.

    Returns:
        str: The translated string, or the key itself if translation not found
    """
    if language not in translations:
        language = DEFAULT_LANGUAGE

    return translations[language].get(key, key)
