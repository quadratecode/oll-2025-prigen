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
import json
from datetime import datetime
from random import randint
import requests

from questions import (
    questions,
    get_question_by_id,
    collect_all_responsible_parties,
    collect_all_processors,
)
from session_manager import SessionManager
from visualizer import DataFlowVisualizer
from policy_generator import PolicyGenerator
from translations import get_text, get_formatted_text, AVAILABLE_LANGUAGES


# Initialize the app
st.set_page_config(
    page_title="Data Flow Assessment Tool",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded",
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
    language = st.session_state.get("language", "de")

    # Handle special question types
    if question["type"] == "special":
        if question.get("special_type") == "responsible_processors":
            return render_responsible_processors_question(question)
        elif question.get("special_type") == "processor_matrix":
            return render_processor_matrix_question(question)
        return False

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
        # For lists, use a more interactive approach instead of comma-separated values
        if question.get("store_as_list", False):
            # Initialize the list in session state if it doesn't exist
            if question_id not in st.session_state.answers:
                st.session_state.answers[question_id] = []

            # maybe_default = question.get("default", [""])
            # if len(maybe_default) > 1 :
            # #     default_value = maybe_default[randint(0, len(maybe_default) - 1)]
            # # elif len(maybe_default) == 1:
            #     default_value = maybe_default[0]
            # else:
            #     default_value = st.session_state.answers.get(question_id, "")
            default_value = st.session_state.answers.get(question_id, "")

            # Create a form for adding new items to avoid widget key conflicts
            with st.form(key=f"add_item_form_{question_id}"):
                new_item = st.text_input(
                    "Neuen Eintrag hinzufügen:",

                    key=f"input_{question_id}",
                    value=default_value,
                    max_chars=question.get(
                        "max_length", 500
                    ),  # Add max_chars constraint
                )
                submitted = st.form_submit_button(get_text("add_button", language))
                if submitted and new_item.strip():
                    print(new_item)
                    if question_id not in st.session_state.answers:
                        st.session_state.answers[question_id] = []
                    st.session_state.answers[question_id].append(new_item.strip())
                    st.rerun()

            # Display the current list of items with delete buttons
            if st.session_state.answers.get(question_id, []):
                st.write(get_text("current_entries", language))
                for i, item_value in enumerate(st.session_state.answers[question_id]):
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.text(item_value)
                    with col2:
                        if st.button("🗑️", key=f"delete_{question_id}_{i}"):
                            st.session_state.answers[question_id].pop(i)
                            st.rerun()
        else:
            # Regular text input for non-list fields
            # maybe_default = question.get("default", [""])
            # if len(maybe_default) > 1 and not st.session_state.answers.get(question_id, ""):
            #     default_value = maybe_default[randint(0, len(maybe_default) - 1)]
            # elif len(maybe_default) == 1 and not st.session_state.answers.get(question_id, ""):
            #     default_value = maybe_default[0]
            # else:
            #     default_value = st.session_state.answers.get(question_id, "")
            default_value = st.session_state.answers.get(question_id, "")

            if question.get("multiline", False):
                user_input = st.text_area(
                    get_text("your_answer", language),
                    value=default_value,
                    key=f"input_{question_id}",
                    height=150,
                    label_visibility="collapsed",
                    max_chars=question.get(
                        "max_length", 500
                    ),  # Add max_chars constraint
                )
            else:
                user_input = st.text_input(
                    get_text("your_answer", language),
                    value=default_value,
                    key=f"input_{question_id}",
                    label_visibility="collapsed",
                    max_chars=question.get(
                        "max_length", 500
                    ),  # Add max_chars constraint
                )

            if user_input:
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
            get_text("select_one", language),
            options,
            index=default_idx,
            key=f"radio_{question_id}",
            label_visibility="collapsed",
        )

        st.session_state.answers[question_id] = selected

    elif question["type"] == "multiple_choice":
        options = question["options"]
        default = []

        if question_id in st.session_state.answers:
            if isinstance(st.session_state.answers[question_id], list):
                default = [
                    opt
                    for opt in st.session_state.answers[question_id]
                    if opt in options
                ]
            else:
                default = (
                    [st.session_state.answers[question_id]]
                    if st.session_state.answers[question_id] in options
                    else []
                )

        selected = st.multiselect(
            get_text("select_all", language),
            options,
            default=default,
            key=f"multiselect_{question_id}",
            # label_visibility="collapsed",
        )

        # Always update the answer state for multiselect to fix the selection issue
        st.session_state.answers[question_id] = selected

    elif question["type"] == "number":
        default_value = st.session_state.answers.get(question_id, 0)
        user_input = st.number_input(
            get_text("your_answer", language),
            value=(
                float(default_value) if isinstance(default_value, (int, float)) else 0
            ),
            key=f"number_{question_id}",
            label_visibility="collapsed",
        )

        st.session_state.answers[question_id] = user_input

    elif question["type"] == "toggle":
        # Add handling for toggle type (yes/no)
        default_value = question.get("default", False)
        if question_id in st.session_state.answers:
            default_value = st.session_state.answers[question_id]

        selected = st.radio(
            get_text("select_one", language),
            ["Ja", "Nein"],
            index=0 if default_value else 1,
            key=f"toggle_{question_id}",
            label_visibility="collapsed",
        )

        # Convert "Ja"/"Nein" to True/False
        selected_value = selected == "Ja"
        st.session_state.answers[question_id] = selected_value

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
        elif question["type"] == "toggle":
            # Toggle questions are always answered once rendered
            is_answered = True

    return is_answered


def render_responsible_processors_question(question):
    """
    Render the special question for processors per responsible party

    Args:
        question (dict): The question configuration

    Returns:
        bool: True if all required sub-questions are answered, False otherwise
    """
    language = st.session_state.get("language", "de")

    st.markdown(f"**{question['text']}**")
    if "help" in question:
        st.caption(question["help"])

    # Collect all responsible parties from previous answers
    responsible_parties = collect_all_responsible_parties(st.session_state.answers)

    if not responsible_parties:
        st.info(get_text("responsible_parties_first", language))
        return False

    all_answered = True

    # Create a section for each responsible party using tabs
    tabs = st.tabs(responsible_parties)

    for i, party in enumerate(responsible_parties):
        with tabs[i]:
            st.markdown(
                f"### {get_formatted_text('processor_for', language, party=party)}"
            )

            question_id = f"processors_{party}"

            # Initialize the list in session state if it doesn't exist
            if question_id not in st.session_state.answers:
                st.session_state.answers[question_id] = []

            # Create a form for adding new processors
            with st.form(key=f"add_processor_form_{question_id}"):
                new_processor = st.text_input(
                    get_text("add_new_processor", language), key=f"input_{question_id}"
                )
                submitted = st.form_submit_button(get_text("add_button", language))
                if submitted and new_processor.strip():
                    if question_id not in st.session_state.answers:
                        st.session_state.answers[question_id] = []
                    st.session_state.answers[question_id].append(new_processor.strip())
                    st.rerun()

            # Display the current list of processors with delete buttons
            if st.session_state.answers.get(question_id, []):
                st.write(get_text("current_processors", language))
                for j, processor in enumerate(st.session_state.answers[question_id]):
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.text(processor)
                    with col2:
                        if st.button("🗑️", key=f"delete_{question_id}_{j}"):
                            st.session_state.answers[question_id].pop(j)
                            st.rerun()

            # Check if this party has at least one processor
            is_answered = len(st.session_state.answers.get(question_id, [])) > 0
            if not is_answered:
                st.warning(get_text("min_one_processor", language))

            all_answered = all_answered and is_answered

    return all_answered


def render_processor_matrix_question(question):
    """
    Render the matrix question for processors, purposes, and data types

    Args:
        question (dict): The question configuration

    Returns:
        bool: True if the matrix has been filled out, False otherwise
    """
    language = st.session_state.get("language", "de")

    st.markdown(f"**{question['text']}**")
    if "help" in question:
        st.caption(question["help"])

    # Collect processors, purposes, and data types
    processors = collect_all_processors(st.session_state.answers)
    purposes = st.session_state.answers.get("processing_purposes", [])
    data_types = st.session_state.answers.get("data_types", [])

    if not processors or not purposes or not data_types:
        st.info(get_text("matrix_no_data", language))
        return False

    # Create matrix UI
    st.markdown(f"### {get_text('processor_matrix_heading', language)}")

    all_answered = True

    # Create a tab for each processor
    tabs = st.tabs(processors)
    for i, processor in enumerate(processors):
        with tabs[i]:
            st.markdown(f"#### {processor}")

            # Add an expander for each purpose to make it more compact
            has_any_checked = False

            for purpose in purposes:
                with st.expander(f"{purpose}", expanded=False):
                    # Create a grid of checkboxes for each data type
                    # Use multiple columns for better layout
                    num_columns = 2  # You can adjust this based on screen size
                    rows = [
                        data_types[j : j + num_columns]
                        for j in range(0, len(data_types), num_columns)
                    ]

                    for row in rows:
                        cols = st.columns(num_columns)
                        for j, data_type in enumerate(row):
                            with cols[j]:
                                question_id = (
                                    f"matrix_{processor}_{purpose}_{data_type}"
                                )

                                checked = st.checkbox(
                                    f"{data_type}",
                                    value=st.session_state.answers.get(
                                        question_id, False
                                    ),
                                    key=f"checkbox_{question_id}",
                                )

                                # Update answer
                                st.session_state.answers[question_id] = checked

                                if checked:
                                    has_any_checked = True

            # Add quick selection buttons only if not hidden
            if not question.get("hide_quick_selection", False):
                st.markdown(f"#### {get_text('quick_selection', language)}")

                # Create select all/none buttons for each purpose
                purpose_cols = st.columns(len(purposes))
                for j, purpose in enumerate(purposes):
                    with purpose_cols[j]:
                        if st.button(
                            get_formatted_text(
                                "select_all_for", language, purpose=purpose
                            ),
                            key=f"select_all_{processor}_{purpose}",
                        ):
                            for data_type in data_types:
                                question_id = (
                                    f"matrix_{processor}_{purpose}_{data_type}"
                                )
                                st.session_state.answers[question_id] = True
                            st.rerun()

                        if st.button(
                            get_formatted_text(
                                "select_none_for", language, purpose=purpose
                            ),
                            key=f"select_none_{processor}_{purpose}",
                        ):
                            for data_type in data_types:
                                question_id = (
                                    f"matrix_{processor}_{purpose}_{data_type}"
                                )
                                st.session_state.answers[question_id] = False
                            st.rerun()

            # Show current selections
            st.markdown(f"#### {get_text('current_selection', language)}")
            selections = []
            for purpose in purposes:
                for data_type in data_types:
                    question_id = f"matrix_{processor}_{purpose}_{data_type}"
                    if st.session_state.answers.get(question_id, False):
                        selections.append(f"**{purpose}**: {data_type}")

            if selections:
                for selection in selections:
                    st.markdown(f"- {selection}")
            else:
                st.info(get_text("no_selection", language))
                all_answered = False

    if not all_answered:
        st.warning(get_text("min_one_selection", language))

    return all_answered


def render_repeated_section(section, answers):
    """
    Render a section of questions repeated for each item in a list

    Args:
        section (dict): The section configuration
        answers (dict): The current answers

    Returns:
        bool: True if all required questions in the section are answered
    """
    language = st.session_state.get("language", "de")

    repeat_for = section["repeat_for"]
    items = answers.get(repeat_for, [])

    if not items:
        field_name = repeat_for.replace("_", " ")
        st.info(get_formatted_text("answer_first", language, field=field_name))
        return False

    all_answered = True

    for item in items:
        st.markdown(get_formatted_text("details_for", language, item=item))
        item = item.strip('"').strip("[").strip("]")
        st.markdown(f"### Details for: **{item}**")
        st.markdown("---")

        for question in section["questions"]:
            # Replace {item} in the question ID
            question_id = (
                question["id"].replace("{item}", item)
                if "{item}" in question["id"]
                else question["id"]
            )

            # Check if this specific instance of the question should be shown
            modified_question = question.copy()
            if "condition" in modified_question:
                modified_question["condition"]["question_id"] = modified_question[
                    "condition"
                ]["question_id"].replace("{item}", item)

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
    language = st.session_state.get("language", "de")

    st.header(get_text("summary_title", language))

    # Prepare data for display
    summary_data = []

    # Process regular questions first
    for question in questions:
        if question["type"] not in ["section", "repeated_section", "special"]:
            if question["id"] in answers:
                answer = answers[question["id"]]

                # Format the answer for display
                if isinstance(answer, list):
                    answer_display = ", ".join(str(a) for a in answer)
                else:
                    answer_display = str(answer)

                summary_data.append(
                    {"Frage": question["text"], "Antwort": answer_display}
                )

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

                        summary_data.append(
                            {"Frage": sub_q["text"], "Antwort": answer_display}
                        )

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
                            modified_question["condition"]["question_id"] = (
                                modified_question["condition"]["question_id"].replace(
                                    "{item}", item
                                )
                            )
                            if not should_show_question(modified_question, answers):
                                continue

                        answer = answers[question_id]

                        # Format the answer for display
                        if isinstance(answer, list):
                            answer_display = ", ".join(str(a) for a in answer)
                        else:
                            answer_display = str(answer)

                        summary_data.append(
                            {
                                "Frage": f"{sub_q['text'].replace('{item}', item)} ({item})",
                                "Antwort": answer_display,
                            }
                        )

        # Process special questions
        elif question["type"] == "special":
            if question["special_type"] == "responsible_processors":
                responsible_parties = collect_all_responsible_parties(answers)
                for party in responsible_parties:
                    question_id = f"processors_{party}"
                    if question_id in answers:
                        processors = answers[question_id]
                        if processors:
                            answer_display = ", ".join(processors)
                            summary_data.append(
                                {
                                    "Frage": get_formatted_text(
                                        "processor_for", language, party=party
                                    ),
                                    "Antwort": answer_display,
                                }
                            )

            elif question["special_type"] == "processor_matrix":
                processors = collect_all_processors(answers)
                purposes = answers.get("processing_purposes", [])
                data_types = answers.get("data_types", [])

                for processor in processors:
                    matrix_entries = []

                    for purpose in purposes:
                        for data_type in data_types:
                            question_id = f"matrix_{processor}_{purpose}_{data_type}"
                            if answers.get(question_id, False):
                                matrix_entries.append(f"{purpose} - {data_type}")

                    if matrix_entries:
                        answer_display = "; ".join(matrix_entries)
                        summary_data.append(
                            {
                                "Frage": get_formatted_text(
                                    "purposes_datatypes_for",
                                    language,
                                    processor=processor,
                                ),
                                "Antwort": answer_display,
                            }
                        )

    # Display as a dataframe
    if summary_data:
        # Translate column headers based on language
        if language == "en":
            for item in summary_data:
                item["Question"] = item.pop("Frage")
                item["Answer"] = item.pop("Antwort")


        llm=False
        df = pd.DataFrame(summary_data)

        if llm:

            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + open(".env").read().rstrip().split("=")[1],
            }

            prompt = """

            Du bist ein Experte für schweizerische Gesetzgebung mit Schwerpunkt Datenschutzrecht. Auf Grundlage der nachfolgenden strukturierten Übersicht sollst du einen kohärenten Gesetzestext in Fließtextform formulieren – orientiert an der sprachlichen und formalen Gestaltung des Schweizer Datenschutzgesetzes (DSG).

            **Anforderungen an die Ausgabe:**

            - Der Gesetzestext soll vollständig als zusammenhängender Fließtext erscheinen – **ohne Bulletpoints, Nummerierungen, Listen oder Tabellen**.
            - Orientiere dich am **juristischen Stil** der schweizerischen Gesetzgebung: sachlich, klar, geschlechtsneutral, präzise.
            - Nutze die nachstehende **strukturierte Gesetzesgliederung** als inhaltliche Orientierung. Die Titel sollen sinngemäß in den Text eingebaut werden – entweder als Überschriften oder eingebettet im Fließtext.
            - Die Begriffe und Inhalte sollen wie bei echten Gesetzestexten in **Artikelstruktur** gegossen sein. Die Abschnitte innerhalb eines Kapitels (z. B. 3.1 und 3.2) dürfen als getrennte Artikel formuliert werden.
            - Kein erklärender Text, keine Kommentare – nur der eigentliche Gesetzestext.

            **Struktur für die Gesetzgebung (als Fließtext umzusetzen):**

            | **Kapitel** | **Bezeichnung**                         |
            | ----------- | --------------------------------------- |
            | 1           | Begriffe, Grundsätze, Systeme           |
            | 2           | Datenkatalog                            |
            | 3           | Datenbearbeitungen, Profiling           |
            | 3.1         | Abschnitt: Datenbearbeitung             |
            | 3.2         | Abschnitt: Profiling                    |
            | 4           | Zugriffsrechte                          |
            | 5           | Datenbekanntgaben                       |
            | 6           | Einschränkungen von Betroffenenrechten  |
            | 7           | Aufbewahrung, Archivierung, Vernichtung |
            | 7.1         | Abschnitt: Aufbewahrung                 |
            | 7.2         | Abschnitt: Archivierung und Vernichtung |

            Ergänze diesen Text so, dass er einer vollständigen Regelung für Organisationen in der Schweiz entspricht – in Anlehnung an das Bundesgesetz über den Datenschutz (DSG) und unter Beachtung der föderalen Rahmenbedingungen. Bitte verwende dafür den folgenden Datensatz:

            ```
            {}
            ```

            Berücksichtige schweizerische Rechtsbegriffe, föderale Zuständigkeiten und formuliere geschlechtsneutral. Bitte aufpassen, dass Headers in der richtige Reihenfolge formatiert werden, und bitte pass auf die differenzierung zwischen kapitel und artikel mit indent.
            """

            json_data = {
                'model': 'llama3.1-8b',
                'stream': False,
                'messages': [
                    {
                        'content': prompt.format(df.to_markdown()),
                        'role': 'user',
                    },
                ],
                'temperature': 0,
                'max_completion_tokens': -1,
                'seed': 0,
                'top_p': 1,
            }

            response = requests.post('https://api.cerebras.ai/v1/chat/completions', headers=headers, json=json_data)
            st.markdown(
            json.loads(response.text)["choices"][0]["message"]["content"]
            )
        else:
            st.dataframe(df, use_container_width=True)
    else:
        st.info(get_text("no_answers", language))


def render_sidebar():
    """Render the sidebar for session management and language selection"""
    language = st.session_state.get("language", "de")

    st.sidebar.title(get_text("sidebar_title", language))
    st.sidebar.markdown("---")

    # Language selection
    st.sidebar.subheader(get_text("language_selection", language))
    language_options = {
        "de": get_text("language_de", language),
        "en": get_text("language_en", language),
    }
    selected_language = st.sidebar.radio(
        label="",
        options=list(language_options.keys()),
        format_func=lambda x: language_options[x],
        index=0 if language == "de" else 1,
        label_visibility="collapsed",
        key="language_selector",
    )

    # Update language in session state if changed
    if selected_language != st.session_state.get("language", "de"):
        st.session_state.language = selected_language
        st.rerun()

    st.sidebar.markdown("---")

    # Session management section
    st.sidebar.header(get_text("session_management", language))

    # Progress indicator
    if not st.session_state.completed:
        current_index = st.session_state.current_question_index
        progress = min(1.0, (current_index + 1) / len(questions))
        st.sidebar.progress(progress)
        st.sidebar.caption(
            get_formatted_text(
                "question_progress",
                language,
                current=current_index + 1,
                total=len(questions),
            )
        )

    # Session actions
    session_action = st.sidebar.radio(
        get_text("session_options", language),
        [
            get_text("continue_session", language),
            get_text("export_session", language),
            get_text("import_session", language),
            get_text("new_session", language),
        ],
    )

    if session_action == get_text("export_session", language):
        # Allow custom naming
        session_name = st.sidebar.text_input(
            get_text("session_name", language),
            help=get_text("auto_name", language),
        )

        # Generate the export data
        file_name, file_content = session_manager.export_session(
            session_name if session_name else None
        )

        # Create download button
        st.sidebar.download_button(
            label=get_text("download_session", language),
            data=file_content,
            file_name=file_name,
            mime="application/json",
            help=get_text("download_help", language),
        )

    elif session_action == get_text("import_session", language):
        # First-stage: File uploader
        uploaded_file = st.sidebar.file_uploader(
            get_text("upload_session", language),
            type=["json"],
            help=get_text("file_upload_help", language),
            key="session_uploader",
        )

        # Second-stage: Only process when button is clicked
        if uploaded_file is not None:
            if st.sidebar.button(
                get_text("import_button", language), key="confirm_import"
            ):
                if session_manager.import_session(uploaded_file):
                    st.sidebar.success(get_text("session_imported", language))
                    # Force refresh to apply the imported session
                    st.rerun()

    elif session_action == get_text("new_session", language):
        if st.sidebar.button(get_text("confirm_new", language)):
            # Reset session state
            session_manager.reset_session()
            st.sidebar.success(get_text("session_reset", language))
            # Force refresh
            st.rerun()

    st.sidebar.markdown("---")

    # Navigation between sections when questionnaire is complete
    if st.session_state.completed:
        st.sidebar.header(get_text("navigation", language))

        view_mode = st.sidebar.radio(
            get_text("view_mode", language),
            [
                get_text("summary_view", language),
                get_text("edit_answers_view", language),
                get_text("visualize_view", language),
                get_text("policy_view", language),
            ],
        )

        return view_mode

    return None


def main():
    """Main application function"""
    language = st.session_state.get("language", "de")

    # st.title(get_text("app_title", language))

    # Initialize visualizer and policy generator
    visualizer = DataFlowVisualizer()
    policy_generator = PolicyGenerator()

    # Render sidebar and get the selected view mode
    view_mode = render_sidebar()

    # If questionnaire is completed, show the selected view
    if st.session_state.completed and view_mode:
        if view_mode == get_text("summary_view", language):
            render_summary(st.session_state.answers)

        elif view_mode == get_text("edit_answers_view", language):
            st.header(get_text("edit_responses", language))
            st.info(get_text("edit_answers_view", language))

            edit_index = st.number_input(
                get_text("edit_question_number", language),
                min_value=1,
                max_value=len(questions),
                value=1,
            )

            # Display the selected question for editing
            current_question = questions[edit_index - 1]

            if current_question["type"] == "repeated_section":
                render_repeated_section(current_question, st.session_state.answers)
            elif current_question["type"] == "section":
                if should_show_question(current_question, st.session_state.answers):
                    render_section(current_question, st.session_state.answers)
                else:
                    st.info(get_text("section_not_applicable", language))
            elif current_question["type"] == "special":
                if current_question.get("special_type") == "responsible_processors":
                    render_responsible_processors_question(current_question)
                elif current_question.get("special_type") == "processor_matrix":
                    render_processor_matrix_question(current_question)
            else:
                render_question(current_question)

            # Add a button to save changes
            if st.button(get_text("save_changes", language)):
                st.success(get_text("changes_saved", language))

        elif view_mode == get_text("visualize_view", language):
            st.header(get_text("visualize", language))
            visualizer.render_visualization(st.session_state.answers)

        elif view_mode == get_text("policy_view", language):
            st.header(get_text("policy_suggestions", language))
            policy_generator.render_policy_suggestions(st.session_state.answers)

    # If questionnaire is not completed or "Edit Responses" is selected, show the questionnaire
    else:
        # Display the current question or section
        current_index = st.session_state.current_question_index

        if current_index < len(questions):
            current_question = questions[current_index]

            all_answered = False

            if current_question["type"] == "repeated_section":
                all_answered = render_repeated_section(
                    current_question, st.session_state.answers
                )
            elif current_question["type"] == "section":
                if should_show_question(current_question, st.session_state.answers):
                    all_answered = render_section(
                        current_question, st.session_state.answers
                    )
                else:
                    # Skip this section
                    st.session_state.current_question_index += 1
                    st.rerun()
            elif current_question["type"] == "special":
                if current_question.get("special_type") == "responsible_processors":
                    all_answered = render_responsible_processors_question(
                        current_question
                    )
                elif current_question.get("special_type") == "processor_matrix":
                    all_answered = render_processor_matrix_question(current_question)
            else:
                all_answered = render_question(current_question)

            # Navigation buttons
            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                if current_index > 0:
                    if st.button(get_text("previous", language)):
                        st.session_state.current_question_index -= 1
                        st.rerun()

            with col3:
                if all_answered:
                    if current_index < len(questions) - 1:
                        if st.button(get_text("next", language)):
                            st.session_state.current_question_index += 1
                            st.rerun()
                    else:
                        if st.button(get_text("complete", language)):
                            st.session_state.completed = True
                            # Remind user to download their session
                            st.success(get_text("completion_success", language))
                            st.rerun()
                else:
                    st.button(get_text("next", language), disabled=True)

                    if current_question["type"] in [
                        "repeated_section",
                        "section",
                        "special",
                    ]:
                        st.warning(get_text("section_required_warning", language))
                    else:
                        required = current_question.get("required", False)
                        if required:
                            st.warning(get_text("required_warning", language))


if __name__ == "__main__":
    main()
