"""
Visualization module for the Data Flow Assessment tool.
Placeholder for future implementation of data flow diagrams.
"""

import streamlit as st
from pathlib import Path
import os
from translations import get_text


class DataFlowVisualizer:
    """
    Placeholder class for generating data flow visualizations.
    """

    def __init__(self, output_dir="visualizations"):
        """
        Initialize the visualizer.

        Args:
            output_dir (str): Directory to store visualization outputs
        """
        self.output_dir = output_dir
        Path(output_dir).mkdir(exist_ok=True)

    def generate_d2_script(self, answers):
        """
        Generate d2lang script from questionnaire answers.

        Args:
            answers (dict): Questionnaire answers

        Returns:
            str: d2lang script content
        """
        language = st.session_state.get("language", "de")

        # Extract relevant data
        systems = answers.get("systems", [])

        # Start building the d2 script
        d2_script = "# Data Flow Diagram\n\n"

        # Add systems as nodes
        d2_script += "# Systems\n"
        for system in systems:
            purpose = answers.get(f"system_purpose_{system}", "")
            d2_script += f"{system}: {system}\\n({purpose}) {{shape: rectangle}}\n"

        # Add responsible parties and processors
        responsible_parties = []
        for system in systems:
            system_responsible = answers.get(f"system_responsible_{system}", [])
            for party in system_responsible:
                if party not in responsible_parties:
                    responsible_parties.append(party)

        if "additional_responsible" in answers:
            for party in answers["additional_responsible"]:
                if party not in responsible_parties:
                    responsible_parties.append(party)

        # Labels based on language
        processor_label = get_text("processor", language)

        d2_script += "\n# Responsible Parties and Processors\n"
        for party in responsible_parties:
            processors = answers.get(f"processors_{party}", [])
            processors_str = ", ".join(processors)
            d2_script += f"{party}: {party}\\n({processor_label}s: {processors_str}) {{shape: oval}}\n"

        # Add data types
        data_types = answers.get("data_types", [])
        d2_script += "\n# Data Types\n"
        d2_script += "data: Data {\n"
        for data_type in data_types:
            categories = answers.get(f"data_categories_{data_type}", [])
            categories_str = ", ".join(
                categories[:2]
            )  # Limit to first 2 categories for readability
            if len(categories) > 2:
                categories_str += "..."

            d2_script += (
                f"  {data_type}: {data_type}\\n({categories_str}) {{shape: document}}\n"
            )
        d2_script += "}\n"

        # Add some connections
        d2_script += "\n# Connections (Placeholder)\n"

        # Simple connection from systems to responsible parties
        for system in systems:
            responsible_parties = answers.get(f"system_responsible_{system}", [])
            for party in responsible_parties:
                d2_script += f"{system} -> {party}\n"

        return d2_script

    def render_visualization(self, answers, output_format="svg"):
        """
        Placeholder for generating and rendering the visualization.

        Args:
            answers (dict): Questionnaire answers
            output_format (str): Output format ("svg", "png")

        Returns:
            str: Message indicating this is a placeholder
        """
        language = st.session_state.get("language", "de")

        # Display a message that this is a placeholder
        st.info(get_text("visualization_placeholder", language))

        # Show a preview of what the d2 script would look like
        d2_script = self.generate_d2_script(answers)
        st.code(d2_script, language="yaml")

        return "placeholder"
