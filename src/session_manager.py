"""
Session management module for the Data Flow Assessment tool.
Handles exporting and importing user sessions via client-side storage.
"""

import json
import streamlit as st
from datetime import datetime
from translations import get_text, get_formatted_text


class SessionManager:
    """
    Manages the session state for the Data Flow Assessment tool.
    Handles export and import of user sessions via client-side downloads/uploads.
    """

    def __init__(self):
        """Initialize the session manager."""
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialize session state variables if they don't exist"""
        if "answers" not in st.session_state:
            st.session_state.answers = {}
        if "current_question_index" not in st.session_state:
            st.session_state.current_question_index = 0
        if "completed" not in st.session_state:
            st.session_state.completed = False
        if "language" not in st.session_state:
            st.session_state.language = "de"  # Default language

    def export_session(self, name=None):
        """
        Prepare current session state for export.

        Args:
            name (str, optional): Name for the session file

        Returns:
            tuple: (file_name, json_content) for download
        """
        # Generate a name based on system name if available, otherwise use timestamp
        if name is None:
            system_name = ""
            if (
                "systems" in st.session_state.answers
                and st.session_state.answers["systems"]
            ):
                system_name = st.session_state.answers["systems"][
                    0
                ]  # Use the first system name

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if system_name:
                # Create a filename-safe version of the system name
                safe_name = "".join(c if c.isalnum() else "_" for c in system_name)
                name = f"{safe_name}_{timestamp}.json"
            else:
                name = f"datenfluss_{timestamp}.json"

        # Ensure file has .json extension
        if not name.endswith(".json"):
            name = f"{name}.json"

        # Clean session state of temporary input keys
        cleaned_answers = {}
        for key, value in st.session_state.answers.items():
            # Skip temporary input keys
            if not key.startswith("new_item_") and not key.startswith("new_processor_"):
                cleaned_answers[key] = value

        data = {
            "answers": cleaned_answers,
            "current_question_index": st.session_state.current_question_index,
            "completed": st.session_state.completed,
            "language": st.session_state.language,  # Save the current language setting
            "timestamp": datetime.now().isoformat(),
        }

        # Convert to JSON string
        json_content = json.dumps(data, indent=2, ensure_ascii=False)

        return name, json_content

    def import_session(self, uploaded_file):
        """
        Import session state from an uploaded file.

        Args:
            uploaded_file (UploadedFile): File uploaded by user

        Returns:
            bool: True if import was successful, False otherwise
        """
        try:
            # Read uploaded file content
            content = uploaded_file.getvalue().decode("utf-8")
            data = json.loads(content)

            # Update session state
            st.session_state.answers = data.get("answers", {})
            st.session_state.current_question_index = data.get(
                "current_question_index", 0
            )
            st.session_state.completed = data.get("completed", False)

            # Import language setting if available
            if "language" in data:
                st.session_state.language = data["language"]

            return True
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            language = st.session_state.get("language", "de")
            st.error(get_formatted_text("import_error", language, error=str(e)))
            return False

    def reset_session(self):
        """Reset the current session state to start from scratch"""
        # Save the current language setting
        current_language = st.session_state.get("language", "de")

        # Clear all session state variables
        for key in list(st.session_state.keys()):
            # Keep only internal Streamlit session variables
            if not key.startswith("_"):
                del st.session_state[key]

        # Reinitialize session state
        self._initialize_session_state()

        # Restore the language setting
        st.session_state.language = current_language
