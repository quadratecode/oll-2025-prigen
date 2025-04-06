"""
Visualization module for the Data Flow Assessment tool.
Uses d2lang to create data flow diagrams based on questionnaire responses.
"""

import subprocess
import tempfile
import os
import streamlit as st
from pathlib import Path

class DataFlowVisualizer:
    """
    Generates data flow visualizations using d2lang based on questionnaire responses.
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
        # Extract relevant data
        system_name = answers.get("system_name", "Unnamed System")
        parties = answers.get("data_parties", [])
        data_attributes = answers.get("data_attributes", [])
        data_flows_text = answers.get("data_flows", "")
        
        # Start building the d2 script
        d2_script = f"# Data Flow Diagram for {system_name}\n\n"
        
        # Add parties as nodes
        d2_script += "# Entities/Parties\n"
        for party in parties:
            party_role = answers.get(f"party_role_{party}", "Unknown")
            party_location = answers.get(f"party_location_{party}", "")
            
            # Different shapes based on role
            if party_role == "Data Subject":
                shape = "person"
            elif party_role == "Data Controller":
                shape = "rectangle"
            elif party_role == "Data Processor":
                shape = "cylinder"
            else:  # Joint Controller or Third Party
                shape = "oval"
            
            label = f"{party}\\n({party_role})"
            if party_location:
                label += f"\\n{party_location}"
            
            d2_script += f"{party}: {label} {{{shape}}}\n"
        
        # Add data attributes section
        d2_script += "\n# Data Attributes\n"
        d2_script += "data: Data {\n"
        
        for attr in data_attributes:
            attr_type = answers.get(f"attribute_type_{attr}", "Unknown")
            
            # Different styles based on data type
            if attr_type == "Special Category (Sensitive) Personal Data":
                style = "stroke: red"
            elif attr_type == "Personal Data":
                style = "stroke: orange"
            else:  # Non-Personal Data
                style = "stroke: blue"
            
            d2_script += f"  {attr}: {attr}\\n({attr_type}) {{{style}}}\n"
        
        d2_script += "}\n"
        
        # Parse the data flows text to create connections
        d2_script += "\n# Data Flows\n"
        
        # Manual parsing of data flows - in a real implementation, 
        # this would be more sophisticated or use structured data
        flows = self._parse_data_flows(data_flows_text, parties)
        
        for flow in flows:
            source = flow.get("source")
            target = flow.get("target")
            attributes = flow.get("attributes", [])
            
            if source and target:
                # Create the connection
                connection = f"{source} -> {target}"
                
                # Add label if attributes specified
                if attributes:
                    attr_list = ", ".join(attributes)
                    d2_script += f'{connection}: "{attr_list}"\n'
                else:
                    d2_script += f"{connection}\n"
        
        return d2_script
    
    def _parse_data_flows(self, flows_text, parties):
        """
        Simple parser for data flows from free text description.
        In a production system, this would be more structured.
        
        Args:
            flows_text (str): Description of data flows
            parties (list): List of parties in the system
            
        Returns:
            list: Parsed flows as dicts with source, target, and attributes
        """
        # This is a very simplistic parser that looks for patterns like:
        # "Party A sends X, Y to Party B"
        # In a real implementation, this would be much more sophisticated
        
        flows = []
        
        if not flows_text:
            return flows
        
        # Split by sentences and lines
        sentences = [s.strip() for s in flows_text.replace('\n', '. ').split('.') if s.strip()]
        
        for sentence in sentences:
            # Look for sending patterns
            sentence = sentence.lower()
            
            # Find the source party
            source = None
            for party in parties:
                if party.lower() in sentence:
                    source = party
                    break
            
            if not source:
                continue
                
            # Find the target party
            target = None
            for party in parties:
                if party.lower() in sentence and party.lower() != source.lower():
                    target = party
                    break
            
            if not source or not target:
                continue
                
            flows.append({
                "source": source,
                "target": target,
                "attributes": []  # In a real implementation, we would extract these
            })
        
        return flows
    
    def render_visualization(self, answers, output_format="svg"):
        """
        Generate and render the d2lang visualization.
        
        Args:
            answers (dict): Questionnaire answers
            output_format (str): Output format ("svg", "png")
            
        Returns:
            str: Path to the generated visualization file
        """
        # Check if d2 is installed
        try:
            subprocess.run(["d2", "--version"], check=True, capture_output=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            st.error("d2lang is not installed or not in PATH. Please install d2lang to use visualization.")
            st.markdown("[Install d2lang](https://d2lang.com/tour/install)")
            return None
        
        # Generate the d2 script
        d2_script = self.generate_d2_script(answers)
        
        # Create a temporary file for the d2 script
        with tempfile.NamedTemporaryFile(mode="w", suffix=".d2", delete=False) as temp_file:
            temp_file.write(d2_script)
            d2_path = temp_file.name
        
        # Create output filename
        system_name = answers.get("system_name", "unnamed_system")
        safe_name = "".join(c if c.isalnum() else "_" for c in system_name)
        output_filename = f"{safe_name}_dataflow.{output_format}"
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Run d2 to generate the visualization
        try:
            subprocess.run(
                ["d2", d2_path, output_path, f"--theme=200", "--pad=50"],
                check=True,
                capture_output=True
            )
            
            # Clean up temp file
            os.unlink(d2_path)
            
            return output_path
        except subprocess.SubprocessError as e:
            st.error(f"Error generating visualization: {str(e)}")
            # Clean up temp file
            os.unlink(d2_path)
            return None

# Example usage in the app:
# visualizer = DataFlowVisualizer()
# svg_path = visualizer.render_visualization(st.session_state.answers)
# if svg_path:
#     with open(svg_path, "r") as f:
#         svg_content = f.read()
#     st.image(svg_content)
