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
    
    def __init__(self, data_dir="data"):
        """
        Initialize the session manager.
        
        Args:
            data_dir (str): Directory to store session data
        """
        self.data_dir = data_dir
        Path(data_dir).mkdir(exist_ok=True)
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state variables if they don't exist"""
        if 'answers' not in st.session_state:
            st.session_state.answers = {}
        if 'current_question_index' not in st.session_state:
            st.session_state.current_question_index = 0
        if 'completed' not in st.session_state:
            st.session_state.completed = False
        if 'session_name' not in st.session_state:
            st.session_state.session_name = None
    
    def save_session(self, name=None):
        """
        Save current session state to a file.
        
        Args:
            name (str, optional): Name for the session file
            
        Returns:
            str: Name of the saved file
        """
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
        
        data = {
            "answers": st.session_state.answers,
            "current_question_index": st.session_state.current_question_index,
            "completed": st.session_state.completed,
            "timestamp": datetime.now().isoformat()
        }
        
        # Ensure file has .json extension
        if not name.endswith(".json"):
            name = f"{name}.json"
        
        filepath = os.path.join(self.data_dir, name)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        # Store the session name
        st.session_state.session_name = name
        
        return name
    
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
            st.session_state.current_question_index = data.get("current_question_index", 0)
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
                    
                    sessions.append({
                        "filename": filename,
                        "system_name": system_name,
                        "timestamp": timestamp,
                        "completed": completed
                    })
                except (json.JSONDecodeError, IOError):
                    # Include corrupt files with minimal info
                    sessions.append({
                        "filename": filename,
                        "system_name": "Error loading file",
                        "timestamp": "Unknown",
                        "completed": False
                    })
        
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
