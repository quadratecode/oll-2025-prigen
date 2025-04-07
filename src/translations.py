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
        "session_exported": "Sitzung erfolgreich exportiert!",
        "session_imported": "Sitzung erfolgreich importiert!",
        "session_reset": "Neue Sitzung gestartet!",
        # Messages
        "required_warning": "Diese Frage ist erforderlich, um fortzufahren.",
        "section_required_warning": "Bitte beantworten Sie alle erforderlichen Fragen in diesem Abschnitt, um fortzufahren.",
        "completion_success": "Bewertung abgeschlossen! Vergessen Sie nicht, Ihre Sitzungsdatei herunterzuladen, um Ihre Arbeit zu speichern.",
        "section_not_applicable": "Dieser Abschnitt ist basierend auf Ihren vorherigen Antworten nicht anwendbar.",
        "import_error": "Fehler beim Importieren der Sitzung: {error}",
        "no_answers": "Noch keine Antworten vorhanden.",
        "changes_saved": "Änderungen erfolgreich gespeichert!",
        # Question-specific help texts and labels
        "your_answer": "Ihre Antwort:",
        "select_one": "Wählen Sie eine Option:",
        "select_all": "Wählen Sie alle zutreffenden Optionen:",
        "add_new_item": "Neuen Eintrag hinzufügen:",
        "add_button": "Hinzufügen",
        "current_entries": "Aktuelle Einträge:",
        "edit_question_number": "Fragennummer zum Bearbeiten:",
        "save_changes": "Änderungen speichern",
        "answer_first": "Bitte beantworten Sie zuerst die Frage zu {field}.",
        # Matrix question
        "processor_matrix_heading": "Bearbeiter, Zweck und Datenarten",
        "processor": "Bearbeiter",
        "purpose": "Zweck",
        "data_type": "Datenart",
        "matrix_select_all": "Alle auswählen",
        "matrix_no_data": "Bitte beantworten Sie zuerst die Fragen zu Bearbeitern, Zwecken und Datenarten.",
        "add_new_processor": "Neuen Bearbeiter hinzufügen:",
        "current_processors": "Aktuelle Bearbeiter:",
        "min_one_processor": "Bitte geben Sie mindestens einen Bearbeiter an.",
        "processor_for": "Bearbeiter für {party}",
        "select_all_for": "Alle für '{purpose}'",
        "select_none_for": "Keine für '{purpose}'",
        "current_selection": "Aktuelle Auswahl",
        "no_selection": "Keine Auswahl getroffen.",
        "min_one_selection": "Bitte wählen Sie für jeden Bearbeiter mindestens eine Kombination aus Zweck und Datenart aus.",
        "details_for": "Details für: {item}",
        "question_progress": "Frage {current} von {total}",
        # View modes
        "summary_view": "Zusammenfassung",
        "edit_answers_view": "Antworten bearbeiten",
        "visualize_view": "Datenflüsse visualisieren",
        "policy_view": "Richtlinienvorschläge",
        "navigation": "Navigation",
        "view_mode": "Ansicht:",
        # Quick selection
        "quick_selection": "Schnellauswahl",
        # Placeholder messages
        "visualization_placeholder": "Die Visualisierungsfunktion ist ein Platzhalter und wird in einem späteren Schritt implementiert.",
        "policy_placeholder": "Die Richtlinienvorschläge sind ein Platzhalter und werden in einem späteren Schritt implementiert.",
        "policy_info": "Dies ist ein Platzhalter für die Richtlinienvorschlagsfunktion. In zukünftigen Versionen werden hier automatisch generierte Richtlinienvorschläge angezeigt.",
        "no_policy_suggestions": "Es konnten keine Richtlinienvorschläge generiert werden. Bitte vervollständigen Sie mehr Fragen im Fragebogen.",
        "policy_recommendations": "Basierend auf Ihren Antworten empfehlen wir die folgenden {count} Richtlinien:",
        "policy_description": "Beschreibung:",
        "policy_recommendations_label": "Empfehlungen:",
        # Session options
        "session_options": "Session-Optionen:",
        # Language selection
        "language_selection": "Sprache:",
        "language_de": "Deutsch",
        "language_en": "Englisch",
        # Purpose and data matrix entries
        "purposes_datatypes_for": "Zwecke und Datenarten für Bearbeiter {processor}",
        # File handling
        "file_upload_help": "Laden Sie eine zuvor exportierte Sitzungsdatei hoch",
        "download_help": "Laden Sie Ihre Sitzung herunter, um später fortzufahren",
        "auto_name": "Lassen Sie das Feld leer für einen automatisch generierten Namen",
        # Responsible parties
        "responsible_parties_first": "Bitte beantworten Sie zuerst die Fragen zu den Verantwortlichen.",
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
        "session_exported": "Session exported successfully!",
        "session_imported": "Session imported successfully!",
        "session_reset": "New session started!",
        # Messages
        "required_warning": "This question is required to proceed.",
        "section_required_warning": "Please answer all required questions in this section to proceed.",
        "completion_success": "Assessment completed! Don't forget to download your session file to save your work.",
        "section_not_applicable": "This section is not applicable based on your previous answers.",
        "import_error": "Error importing session: {error}",
        "no_answers": "No answers available yet.",
        "changes_saved": "Changes saved successfully!",
        # Question-specific help texts and labels
        "your_answer": "Your answer:",
        "select_one": "Select one:",
        "select_all": "Select all that apply:",
        "add_new_item": "Add new entry:",
        "add_button": "Add",
        "current_entries": "Current entries:",
        "edit_question_number": "Question number to edit:",
        "save_changes": "Save Changes",
        "answer_first": "Please answer the question about {field} first.",
        # Matrix question
        "processor_matrix_heading": "Processors, Purposes and Data Types",
        "processor": "Processor",
        "purpose": "Purpose",
        "data_type": "Data Type",
        "matrix_select_all": "Select All",
        "matrix_no_data": "Please answer the questions about processors, purposes, and data types first.",
        "add_new_processor": "Add new processor:",
        "current_processors": "Current processors:",
        "min_one_processor": "Please specify at least one processor.",
        "processor_for": "Processors for {party}",
        "select_all_for": "All for '{purpose}'",
        "select_none_for": "None for '{purpose}'",
        "current_selection": "Current Selection",
        "no_selection": "No selection made.",
        "min_one_selection": "Please select at least one combination of purpose and data type for each processor.",
        "details_for": "Details for: {item}",
        "question_progress": "Question {current} of {total}",
        # View modes
        "summary_view": "Summary",
        "edit_answers_view": "Edit Answers",
        "visualize_view": "Visualize Data Flows",
        "policy_view": "Policy Suggestions",
        "navigation": "Navigation",
        "view_mode": "View:",
        # Quick selection
        "quick_selection": "Quick Selection",
        # Placeholder messages
        "visualization_placeholder": "The visualization feature is a placeholder and will be implemented in a later step.",
        "policy_placeholder": "The policy suggestions are a placeholder and will be implemented in a later step.",
        "policy_info": "This is a placeholder for the policy suggestion feature. In future versions, automatically generated policy suggestions will be displayed here.",
        "no_policy_suggestions": "No policy suggestions could be generated. Please complete more questions in the questionnaire.",
        "policy_recommendations": "Based on your answers, we recommend the following {count} policies:",
        "policy_description": "Description:",
        "policy_recommendations_label": "Recommendations:",
        # Session options
        "session_options": "Session Options:",
        # Language selection
        "language_selection": "Language:",
        "language_de": "German",
        "language_en": "English",
        # Purpose and data matrix entries
        "purposes_datatypes_for": "Purposes and data types for processor {processor}",
        # File handling
        "file_upload_help": "Upload a previously exported session file",
        "download_help": "Download your session to continue later",
        "auto_name": "Leave empty for an automatically generated name",
        # Responsible parties
        "responsible_parties_first": "Please answer the questions about responsible parties first.",
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


def get_formatted_text(key, language=DEFAULT_LANGUAGE, **kwargs):
    """
    Get a translated string and format it with the provided keyword arguments.

    Args:
        key (str): The translation key
        language (str, optional): The language code. Defaults to DEFAULT_LANGUAGE.
        **kwargs: Format arguments to substitute in the translated string

    Returns:
        str: The formatted translated string, or the key itself if translation not found
    """
    text = get_text(key, language)
    try:
        return text.format(**kwargs)
    except (KeyError, ValueError):
        return text
