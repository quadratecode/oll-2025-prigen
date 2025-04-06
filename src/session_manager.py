"""
Session management module for the Data Flow Assessment tool.
Handles saving, loading, and managing user sessions.
"""

import json
import os
import streamlit as st
from datetime import datetime
from pathlib import Path


class SessionManager:
    """
    Manages the session state for the Data Flow Assessment tool.
    Handles persistence, loading and saving of user sessions.
    """

    def __init__(self, use_local_storage=False, data_dir="data"):
        """
        Initialize the session manager.

        Args:
            use_local_storage (bool): Whether to store sessions on disk (default: False)
            data_dir (str): Directory to store session data if local storage is enabled
        """
        self.use_local_storage = use_local_storage
        self.data_dir = data_dir

        # Only create the directory if local storage is enabled
        if self.use_local_storage:
            Path(data_dir).mkdir(exist_ok=True)

        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialize session state variables if they don't exist"""
        if "answers" not in st.session_state:
            st.session_state.answers = {}
        if "current_question_index" not in st.session_state:
            st.session_state.current_question_index = 0
        if "completed" not in st.session_state:
            st.session_state.completed = False
        if "session_name" not in st.session_state:
            st.session_state.session_name = None

    def save_session(self, name=None):
        """
        Save current session state to a file. Only used if local storage is enabled.

        Args:
            name (str, optional): Name for the session file

        Returns:
            str: Name of the saved file, or None if local storage is disabled
        """
        if not self.use_local_storage:
            st.warning("Local storage is disabled. Use 'Download Session' instead.")
            return None

        if name is None:
            if st.session_state.session_name:
                name = st.session_state.session_name
            else:
                # Generate a name based on system name if available, otherwise use timestamp
                system_name = st.session_state.answers.get("system_name", "")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                if system_name:
                    # Create a filename-safe version of the system name
                    safe_name = "".join(c if c.isalnum() else "_" for c in system_name)
                    name = f"{safe_name}_{timestamp}.json"
                else:
                    name = f"session_{timestamp}.json"

        data = self._prepare_session_data()

        # Ensure file has .json extension
        if not name.endswith(".json"):
            name = f"{name}.json"

        filepath = os.path.join(self.data_dir, name)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        # Store the session name
        st.session_state.session_name = name

        return name

    def _prepare_session_data(self):
        """
        Prepare the session data for export or saving.

        Returns:
            dict: Session data dictionary
        """
        return {
            "answers": st.session_state.answers,
            "current_question_index": st.session_state.current_question_index,
            "completed": st.session_state.completed,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0",  # Adding version for future compatibility
        }

    def export_session(self):
        """
        Export the current session as a JSON string for downloading.

        Returns:
            str: JSON string of the session data
        """
        data = self._prepare_session_data()
        return json.dumps(data, indent=2)

    def import_session(self, json_str):
        """
        Import a session from a JSON string (from uploaded file).

        Args:
            json_str (str): JSON string containing session data

        Returns:
            bool: True if import was successful, False otherwise
        """
        try:
            data = json.loads(json_str)

            # Validate the data structure
            required_keys = ["answers", "current_question_index", "completed"]
            if not all(key in data for key in required_keys):
                st.error("Invalid session file format. Missing required fields.")
                return False

            # Perform basic security validation
            if not self._validate_session_data(data):
                st.error("The uploaded file contains potentially unsafe data.")
                return False

            # Load the data into session state
            st.session_state.answers = data.get("answers", {})
            st.session_state.current_question_index = data.get(
                "current_question_index", 0
            )
            st.session_state.completed = data.get("completed", False)

            # Only save to disk if local storage is enabled
            if self.use_local_storage:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                system_name = st.session_state.answers.get("system_name", "")
                if system_name:
                    safe_name = "".join(c if c.isalnum() else "_" for c in system_name)
                    session_name = f"{safe_name}_imported_{timestamp}.json"
                else:
                    session_name = f"imported_session_{timestamp}.json"

                st.session_state.session_name = session_name
                self.save_session(session_name)
            else:
                # Just generate a session name for reference but don't save to disk
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                system_name = st.session_state.answers.get("system_name", "")
                if system_name:
                    safe_name = "".join(c if c.isalnum() else "_" for c in system_name)
                    session_name = f"{safe_name}_imported_{timestamp}"
                else:
                    session_name = f"imported_session_{timestamp}"

                st.session_state.session_name = session_name

            return True
        except json.JSONDecodeError:
            st.error("Invalid JSON format in the uploaded file.")
            return False
        except Exception as e:
            st.error(f"Error importing session: {str(e)}")
            return False

    def _validate_session_data(self, data):
        """
        Validate session data for security concerns.

        Args:
            data (dict): Session data to validate

        Returns:
            bool: True if the data is valid and safe, False otherwise
        """
        # Validate that answers only contains simple data types
        if not isinstance(data.get("answers", {}), dict):
            return False

        # Check answer values to ensure they are basic types
        for key, value in data.get("answers", {}).items():
            # Only allow strings, numbers, booleans, and lists of strings
            if not isinstance(value, (str, int, float, bool, list, dict)):
                return False

            # If it's a list, check that it only contains simple types
            if isinstance(value, list):
                if not all(isinstance(item, (str, int, float, bool)) for item in value):
                    return False

            # If it's a dict, check it only contains simple types
            if isinstance(value, dict):
                if not all(
                    isinstance(v, (str, int, float, bool, list)) for v in value.values()
                ):
                    return False

        # Check that current_question_index is a reasonable number
        if not isinstance(data.get("current_question_index", 0), int):
            return False

        # Check that completed is a boolean
        if not isinstance(data.get("completed", False), bool):
            return False

        return True

    def load_session(self, name):
        """
        Load session state from a file. Only used if local storage is enabled.

        Args:
            name (str): Name of the session file to load

        Returns:
            bool: True if loading was successful, False otherwise
        """
        if not self.use_local_storage:
            st.warning("Local storage is disabled. Use 'Upload Session' instead.")
            return False

        filepath = os.path.join(self.data_dir, name)

        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            # Validate the loaded data for security
            if not self._validate_session_data(data):
                st.error("The session file contains potentially unsafe data.")
                return False

            st.session_state.answers = data.get("answers", {})
            st.session_state.current_question_index = data.get(
                "current_question_index", 0
            )
            st.session_state.completed = data.get("completed", False)
            st.session_state.session_name = name

            return True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            st.error(f"Error loading session: {str(e)}")
            return False

    def list_saved_sessions(self):
        """
        List all saved session files with their metadata. Only used if local storage is enabled.

        Returns:
            list: List of dictionaries with session metadata, or empty list if local storage is disabled
        """
        if not self.use_local_storage:
            return []

        sessions = []

        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)

                    # Extract basic info
                    system_name = data.get("answers", {}).get("system_name", "Unnamed")
                    timestamp = data.get("timestamp", "Unknown date")
                    completed = data.get("completed", False)

                    # Format timestamp for display if available
                    try:
                        if timestamp != "Unknown date":
                            dt = datetime.fromisoformat(timestamp)
                            timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except (ValueError, TypeError):
                        pass

                    sessions.append(
                        {
                            "filename": filename,
                            "system_name": system_name,
                            "timestamp": timestamp,
                            "completed": completed,
                        }
                    )
                except (json.JSONDecodeError, IOError):
                    # Include corrupt files with minimal info
                    sessions.append(
                        {
                            "filename": filename,
                            "system_name": "Error loading file",
                            "timestamp": "Unknown",
                            "completed": False,
                        }
                    )

        # Sort by timestamp (newest first)
        sessions.sort(key=lambda x: x["timestamp"], reverse=True)
        return sessions

    def delete_session(self, name):
        """
        Delete a saved session file. Only used if local storage is enabled.

        Args:
            name (str): Name of the session file to delete

        Returns:
            bool: True if deletion was successful, False if local storage is disabled or on error
        """
        if not self.use_local_storage:
            return False

        filepath = os.path.join(self.data_dir, name)

        try:
            os.remove(filepath)

            # If we deleted the current session, reset the session name
            if st.session_state.session_name == name:
                st.session_state.session_name = None

            return True
        except FileNotFoundError:
            return False

    def reset_session(self):
        """Reset the current session state to start from scratch"""
        st.session_state.answers = {}
        st.session_state.current_question_index = 0
        st.session_state.completed = False
        st.session_state.session_name = None

    def load_session(self, name):
        """
        Load session state from a file.

        Args:
            name (str): Name of the session file to load

        Returns:
            bool: True if loading was successful, False otherwise
        """
        filepath = os.path.join(self.data_dir, name)

        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            st.session_state.answers = data.get("answers", {})
            st.session_state.current_question_index = data.get(
                "current_question_index", 0
            )
            st.session_state.completed = data.get("completed", False)
            st.session_state.session_name = name

            return True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            st.error(f"Error loading session: {str(e)}")
            return False

    def list_saved_sessions(self):
        """
        List all saved session files with their metadata.

        Returns:
            list: List of dictionaries with session metadata
        """
        sessions = []

        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)

                    # Extract basic info
                    system_name = data.get("answers", {}).get("system_name", "Unnamed")
                    timestamp = data.get("timestamp", "Unknown date")
                    completed = data.get("completed", False)

                    # Format timestamp for display if available
                    try:
                        if timestamp != "Unknown date":
                            dt = datetime.fromisoformat(timestamp)
                            timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except (ValueError, TypeError):
                        pass

                    sessions.append(
                        {
                            "filename": filename,
                            "system_name": system_name,
                            "timestamp": timestamp,
                            "completed": completed,
                        }
                    )
                except (json.JSONDecodeError, IOError):
                    # Include corrupt files with minimal info
                    sessions.append(
                        {
                            "filename": filename,
                            "system_name": "Error loading file",
                            "timestamp": "Unknown",
                            "completed": False,
                        }
                    )

        # Sort by timestamp (newest first)
        sessions.sort(key=lambda x: x["timestamp"], reverse=True)
        return sessions

    def delete_session(self, name):
        """
        Delete a saved session file.

        Args:
            name (str): Name of the session file to delete

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        filepath = os.path.join(self.data_dir, name)

        try:
            os.remove(filepath)

            # If we deleted the current session, reset the session name
            if st.session_state.session_name == name:
                st.session_state.session_name = None

            return True
        except FileNotFoundError:
            return False

    def reset_session(self):
        """Reset the current session state to start from scratch"""
        st.session_state.answers = {}
        st.session_state.current_question_index = 0
        st.session_state.completed = False
        st.session_state.session_name = None
