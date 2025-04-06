"""
Data Flow Assessment Tool

A Streamlit application to:
1. Assess data flows through a questionnaire with branching logic
2. Visualize data flows using d2lang
3. Generate policy suggestions based on answers
"""

import streamlit as st
import pandas as pd
import os
from questions import questions, get_question_by_id
from session_manager import SessionManager
from visualizer import DataFlowVisualizer
from policy_generator import PolicyGenerator

# Initialize the app
st.set_page_config(
    page_title="Data Flow Assessment Tool",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session manager
session_manager = SessionManager()

def format_question_text(text, item=None):
    """Format question text by replacing {item} with the actual item"""
    if item and "{item}" in text:
        return text.replace("{item}", item)
    return text

def should_show_question(question, answers):
    """
    Determine if a question should be shown based on its conditions
    
    Args:
        question (dict): The question to check
        answers (dict): The current answers
        
    Returns:
        bool: True if the question should be shown, False otherwise
    """
    if "condition" not in question:
        return True
        
    condition = question["condition"]
    q_id = condition["question_id"]
    operator = condition["operator"]
    value = condition["value"]
    
    if q_id not in answers:
        return False
        
    answer = answers[q_id]
    
    if operator == "==":
        return answer == value
    elif operator == "!=":
        return answer != value
    elif operator == "in":
        return answer in value if isinstance(value, list) else False
    elif operator == "contains":
        return value in answer if isinstance(answer, list) else answer == value
    
    return True

def render_question(question, item=None):
    """
    Render a question based on its type
    
    Args:
        question (dict): The question to render
        item (str, optional): The item for a repeated question
        
    Returns:
        bool: True if the question has been answered, False otherwise
    """
    question_id = question["id"]
    if item and "{item}" in question_id:
        question_id = question_id.replace("{item}", item)
    
    question_text = format_question_text(question["text"], item)
    
    # Show help text if available
    if "help" in question:
        st.markdown(f"**{question_text}**")
        st.caption(question["help"])
    else:
        st.markdown(f"**{question_text}**")
    
    if question["type"] == "text":
        default_value = st.session_state.answers.get(question_id, "")
        
        if question.get("multiline", False):
            user_input = st.text_area(
                "Your answer:",
                value=default_value,
                key=f"input_{question_id}",
                height=150,
                label_visibility="collapsed"
            )
        else:
            user_input = st.text_input(
                "Your answer:",
                value=default_value,
                key=f"input_{question_id}",
                label_visibility="collapsed"
            )
        
        if user_input:
            if question.get("store_as_list", False):
                st.session_state.answers[question_id] = [
                    item.strip() for item in user_input.split(",") if item.strip()
                ]
            else:
                st.session_state.answers[question_id] = user_input
    
    elif question["type"] == "single_choice":
        options = question["options"]
        default_idx = 0
        
        if question_id in st.session_state.answers:
            try:
                default_idx = options.index(st.session_state.answers[question_id])
            except ValueError:
                default_idx = 0
        
        selected = st.radio(
            "Select one:",
            options,
            index=default_idx,
            key=f"radio_{question_id}",
            label_visibility="collapsed"
        )
        
        st.session_state.answers[question_id] = selected
    
    elif question["type"] == "multiple_choice":
        options = question["options"]
        default = []
        
        if question_id in st.session_state.answers:
            if isinstance(st.session_state.answers[question_id], list):
                default = [opt for opt in st.session_state.answers[question_id] if opt in options]
            else:
                default = [st.session_state.answers[question_id]] if st.session_state.answers[question_id] in options else []
        
        selected = st.multiselect(
            "Select all that apply:",
            options,
            default=default,
            key=f"multiselect_{question_id}",
            label_visibility="collapsed"
        )
        
        if selected or not question.get("required", False):
            st.session_state.answers[question_id] = selected
    
    elif question["type"] == "number":
        default_value = st.session_state.answers.get(question_id, 0)
        user_input = st.number_input(
            "Your answer:",
            value=float(default_value) if isinstance(default_value, (int, float)) else 0,
            key=f"number_{question_id}",
            label_visibility="collapsed"
        )
        
        st.session_state.answers[question_id] = user_input
    
    # Return if the question has been answered and meets requirements
    is_answered = question_id in st.session_state.answers
    
    if question.get("required", False) and is_answered:
        answer = st.session_state.answers[question_id]
        
        if question["type"] == "multiple_choice":
            is_answered = len(answer) > 0
        elif question["type"] == "text":
            is_answered = bool(answer)
            if question.get("store_as_list", False):
                is_answered = len(answer) > 0
    
    return is_answered

def render_repeated_section(section, answers):
    """
    Render a section of questions repeated for each item in a list
    
    Args:
        section (dict): The section configuration
        answers (dict): The current answers
        
    Returns:
        bool: True if all required questions in the section are answered
    """
    repeat_for = section["repeat_for"]
    items = answers.get(repeat_for, [])
    
    if not items:
        st.info(f"Please first answer the question about {repeat_for.replace('_', ' ')} to proceed.")
        return False
    
    all_answered = True
    
    for item in items:
        st.markdown(f"### Details for: **{item}**")
        st.markdown("---")
        
        for question in section["questions"]:
            # Replace {item} in the question ID
            question_id = question["id"].replace("{item}", item) if "{item}" in question["id"] else question["id"]
            
            # Check if this specific instance of the question should be shown
            modified_question = question.copy()
            if "condition" in modified_question:
                modified_question["condition"]["question_id"] = modified_question["condition"]["question_id"].replace("{item}", item)
            
            if should_show_question(modified_question, answers):
                is_answered = render_question(question, item)
                all_answered = all_answered and is_answered
            
        st.markdown("---")
    
    return all_answered

def render_section(section, answers):
    """
    Render a section of questions
    
    Args:
        section (dict): The section configuration
        answers (dict): The current answers
        
    Returns:
        bool: True if all required questions in the section are answered
    """
    all_answered = True
    
    for question in section["questions"]:
        if should_show_question(question, answers):
            is_answered = render_question(question)
            all_answered = all_answered and is_answered
    
    return all_answered

def render_summary(answers):
    """
    Render a summary of all answers
    
    Args:
        answers (dict): The current answers
    """
    st.header("Summary of Responses")
    
    # Prepare data for display
    summary_data = []
    
    # Process regular questions first
    for question in questions:
        if question["type"] not in ["section", "repeated_section"]:
            if question["id"] in answers:
                answer = answers[question["id"]]
                
                # Format the answer for display
                if isinstance(answer, list):
                    answer_display = ", ".join(str(a) for a in answer)
                else:
                    answer_display = str(answer)
                    
                summary_data.append({
                    "Question": question["text"],
                    "Answer": answer_display
                })
        
        # Process sections
        elif question["type"] == "section":
            if should_show_question(question, answers):
                for sub_q in question["questions"]:
                    if sub_q["id"] in answers:
                        answer = answers[sub_q["id"]]
                        
                        # Format the answer for display
                        if isinstance(answer, list):
                            answer_display = ", ".join(str(a) for a in answer)
                        else:
                            answer_display = str(answer)
                            
                        summary_data.append({
                            "Question": sub_q["text"],
                            "Answer": answer_display
                        })
        
        # Process repeated sections
        elif question["type"] == "repeated_section":
            repeat_for = question["repeat_for"]
            items = answers.get(repeat_for, [])
            
            for item in items:
                for sub_q in question["questions"]:
                    question_id = sub_q["id"].replace("{item}", item)
                    
                    if question_id in answers:
                        # Skip questions that shouldn't be shown based on conditions
                        modified_question = sub_q.copy()
                        if "condition" in modified_question:
                            modified_question["condition"]["question_id"] = modified_question["condition"]["question_id"].replace("{item}", item)
                            if not should_show_question(modified_question, answers):
                                continue
                        
                        answer = answers[question_id]
                        
                        # Format the answer for display
                        if isinstance(answer, list):
                            answer_display = ", ".join(str(a) for a in answer)
                        else:
                            answer_display = str(answer)
                            
                        summary_data.append({
                            "Question": f"{sub_q['text'].replace('{item}', item)} ({item})",
                            "Answer": answer_display
                        })
    
    # Display as a dataframe
    if summary_data:
        df = pd.DataFrame(summary_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No responses yet.")

def render_sidebar():
    """Render the sidebar for session management"""
    st.sidebar.title("Data Flow Assessment")
    st.sidebar.markdown("---")
    
    # Session management section
    st.sidebar.header("Session Management")
    
    # Progress indicator
    if not st.session_state.completed:
        current_index = st.session_state.current_question_index
        progress = min(1.0, (current_index + 1) / len(questions))
        st.sidebar.progress(progress)
        st.sidebar.caption(f"Question {current_index + 1} of {len(questions)}")
    
    # Session actions
    session_action = st.sidebar.radio(
        "Session Options:",
        ["Continue Current Session", "Save Session", "Load Session", "Start New Session"]
    )
    
    if session_action == "Save Session":
        # Allow custom naming
        session_name = st.sidebar.text_input(
            "Session name (optional):",
            value=st.session_state.get("session_name", ""),
            help="Leave blank for auto-generated name"
        )
        
        if st.sidebar.button("Save"):
            name = session_manager.save_session(session_name if session_name else None)
            st.sidebar.success(f"Session saved as: {name}")
            # Force refresh
            st.rerun()
    
    elif session_action == "Load Session":
        sessions = session_manager.list_saved_sessions()
        
        if sessions:
            # Create a user-friendly display of the sessions
            session_options = [f"{s['system_name']} ({s['timestamp']})" for s in sessions]
            session_filenames = [s["filename"] for s in sessions]
            
            selected_index = st.sidebar.selectbox(
                "Select a session to load:",
                range(len(session_options)),
                format_func=lambda i: session_options[i]
            )
            
            selected_filename = session_filenames[selected_index]
            
            if st.sidebar.button("Load Selected Session"):
                if session_manager.load_session(selected_filename):
                    st.sidebar.success(f"Session '{session_options[selected_index]}' loaded!")
                    # Force refresh
                    st.rerun()
            
            # Add option to delete sessions
            if st.sidebar.button("Delete Selected Session"):
                if session_manager.delete_session(selected_filename):
                    st.sidebar.success(f"Session deleted!")
                    # Force refresh
                    st.rerun()
        else:
            st.sidebar.info("No saved sessions found.")
    
    elif session_action == "Start New Session":
        if st.sidebar.button("Confirm New Session"):
            # Save current session if it has data
            if st.session_state.answers:
                session_manager.save_session()
            
            # Reset session state
            session_manager.reset_session()
            st.sidebar.success("New session started!")
            # Force refresh
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # Navigation between sections when questionnaire is complete
    if st.session_state.completed:
        st.sidebar.header("Navigation")
        
        view_mode = st.sidebar.radio(
            "View:",
            ["Summary", "Edit Responses", "Visualize Data Flows", "Policy Suggestions"]
        )
        
        return view_mode
    
    return None

def main():
    """Main application function"""
    st.title("Data Flow Assessment Tool")
    
    # Initialize visualizer and policy generator
    visualizer = DataFlowVisualizer()
    policy_generator = PolicyGenerator()
    
    # Render sidebar and get the selected view mode
    view_mode = render_sidebar()
    
    # If questionnaire is completed, show the selected view
    if st.session_state.completed and view_mode:
        if view_mode == "Summary":
            render_summary(st.session_state.answers)
        
        elif view_mode == "Edit Responses":
            st.header("Edit Responses")
            st.info("You can edit any of your previous responses below.")
            
            edit_index = st.number_input(
                "Question number to edit:",
                min_value=1,
                max_value=len(questions),
                value=1
            )
            
            # Display the selected question for editing
            current_question = questions[edit_index - 1]
            
            if current_question["type"] == "repeated_section":
                render_repeated_section(current_question, st.session_state.answers)
            elif current_question["type"] == "section":
                if should_show_question(current_question, st.session_state.answers):
                    render_section(current_question, st.session_state.answers)
                else:
                    st.info("This section is not applicable based on your previous answers.")
            else:
                render_question(current_question)
                
            # Add a button to save changes
            if st.button("Save Changes"):
                session_manager.save_session()
                st.success("Changes saved successfully!")
        
        elif view_mode == "Visualize Data Flows":
            st.header("Data Flow Visualization")
            
            # Check if we have required data for visualization
            if not st.session_state.answers.get("data_parties") or not st.session_state.answers.get("data_attributes"):
                st.warning("To generate a visualization, please complete the questions about parties and data attributes.")
            else:
                st.write("This visualization shows the data flows between parties in your system.")
                
                # Offer customization options
                col1, col2 = st.columns(2)
                with col1:
                    output_format = st.selectbox(
                        "Output format:",
                        ["svg", "png"],
                        index=0
                    )
                
                # Generate visualization button
                if st.button("Generate Visualization"):
                    with st.spinner("Generating data flow diagram..."):
                        # First display a preview of the d2 script
                        d2_script = visualizer.generate_d2_script(st.session_state.answers)
                        
                        with st.expander("View D2 Script", expanded=False):
                            st.code(d2_script, language="yaml")
                        
                        # Try to generate the visualization
                        try:
                            output_path = visualizer.render_visualization(
                                st.session_state.answers, 
                                output_format=output_format
                            )
                            
                            if output_path and os.path.exists(output_path):
                                if output_format == "svg":
                                    with open(output_path, "r") as f:
                                        svg_content = f.read()
                                    st.components.v1.html(svg_content, height=600)
                                else:  # PNG
                                    st.image(output_path)
                                
                                # Download button for the visualization
                                with open(output_path, "rb") as file:
                                    file_content = file.read()
                                
                                filename = os.path.basename(output_path)
                                st.download_button(
                                    label=f"Download {output_format.upper()} Diagram",
                                    data=file_content,
                                    file_name=filename,
                                    mime=f"image/{output_format}"
                                )
                            else:
                                st.error("Failed to generate the visualization.")
                                st.info("Please make sure d2lang is installed. Run `brew install d2` on macOS or follow installation instructions at https://d2lang.com/tour/install")
                        except Exception as e:
                            st.error(f"Error generating visualization: {str(e)}")
        
        elif view_mode == "Policy Suggestions":
            st.header("Policy Suggestions")
            
            # Generate and display policy suggestions
            if not st.session_state.answers:
                st.warning("Please complete the questionnaire to receive policy suggestions.")
            else:
                # Render policy suggestions
                policy_generator.render_policy_suggestions(st.session_state.answers)
                
                # Add export options
                st.markdown("---")
                st.subheader("Export Policy Suggestions")
                
                export_format = st.selectbox(
                    "Export format:",
                    ["markdown", "csv", "json"],
                    index=0
                )
                
                if st.button("Export"):
                    exported_content = policy_generator.export_policy_suggestions(
                        st.session_state.answers,
                        format=export_format
                    )
                    
                    # Determine file extension and mime type
                    if export_format == "markdown":
                        file_ext = "md"
                        mime = "text/markdown"
                    elif export_format == "csv":
                        file_ext = "csv"
                        mime = "text/csv"
                    else:  # JSON
                        file_ext = "json"
                        mime = "application/json"
                    
                    # Create download button
                    system_name = st.session_state.answers.get("system_name", "system")
                    safe_name = "".join(c if c.isalnum() else "_" for c in system_name)
                    filename = f"{safe_name}_policies.{file_ext}"
                    
                    st.download_button(
                        label=f"Download {export_format.upper()} File",
                        data=exported_content,
                        file_name=filename,
                        mime=mime
                    )
    
    # If questionnaire is not completed or "Edit Responses" is selected, show the questionnaire
    else:
        # Display the current question or section
        current_index = st.session_state.current_question_index
        
        if current_index < len(questions):
            current_question = questions[current_index]
            
            all_answered = False
            
            if current_question["type"] == "repeated_section":
                all_answered = render_repeated_section(
                    current_question, 
                    st.session_state.answers
                )
            elif current_question["type"] == "section":
                if should_show_question(current_question, st.session_state.answers):
                    all_answered = render_section(
                        current_question, 
                        st.session_state.answers
                    )
                else:
                    # Skip this section
                    st.session_state.current_question_index += 1
                    st.rerun()
            else:
                all_answered = render_question(current_question)
            
            # Navigation buttons
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if current_index > 0:
                    if st.button("⬅️ Previous"):
                        st.session_state.current_question_index -= 1
                        st.rerun()
            
            with col3:
                if all_answered:
                    if current_index < len(questions) - 1:
                        if st.button("Next ➡️"):
                            st.session_state.current_question_index += 1
                            st.rerun()
                    else:
                        if st.button("Complete ✅"):
                            st.session_state.completed = True
                            # Save session automatically on completion
                            session_manager.save_session()
                            st.rerun()
                else:
                    st.button("Next ➡️", disabled=True)
                    
                    if current_question["type"] in ["repeated_section", "section"]:
                        st.warning("Please answer all required questions in this section to proceed.")
                    else:
                        required = current_question.get("required", False)
                        if required:
                            st.warning("This question is required to proceed.")

if __name__ == "__main__":
    main()
