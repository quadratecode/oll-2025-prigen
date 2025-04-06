"""
Policy suggestion module for the Data Flow Assessment tool.
Generates policy recommendations based on questionnaire responses.
"""

import streamlit as st
import pandas as pd

class PolicyGenerator:
    """
    Generates policy suggestions based on the answers to the questionnaire.
    """
    
    def __init__(self):
        """Initialize the policy generator."""
        # Load policy rules and templates
        self.policy_rules = self._load_policy_rules()
    
    def _load_policy_rules(self):
        """
        Load policy rules from a predefined set.
        In a production system, these could be loaded from a database or file.
        
        Returns:
            list: List of policy rule dictionaries
        """
        return [
            {
                "id": "gdpr_applicability",
                "condition": lambda answers: any(
                    loc.lower() in ["eu", "eea", "european union", "europe"] 
                    for loc in [answers.get(f"party_location_{party}", "") 
                               for party in answers.get("data_parties", [])]
                ),
                "policy": "GDPR Compliance",
                "description": "Your system processes data of EU/EEA individuals or operates in the EU, "
                              "requiring GDPR compliance.",
                "recommendations": [
                    "Appoint a Data Protection Officer (DPO) if required",
                    "Implement a robust consent management mechanism",
                    "Conduct Data Protection Impact Assessments (DPIA) for high-risk processing",
                    "Ensure data subject rights are properly addressed (access, rectification, erasure, etc.)",
                    "Maintain records of processing activities"
                ]
            },
            {
                "id": "special_category_data",
                "condition": lambda answers: any(
                    answers.get(f"attribute_type_{attr}", "") == "Special Category (Sensitive) Personal Data"
                    for attr in answers.get("data_attributes", [])
                ),
                "policy": "Special Category Data Protection",
                "description": "Your system processes special category (sensitive) personal data, "
                              "requiring additional safeguards and legal basis.",
                "recommendations": [
                    "Ensure explicit consent or another specific legal basis for processing special category data",
                    "Implement stronger security measures for sensitive data",
                    "Minimize the collection and retention of sensitive data",
                    "Consider pseudonymization or anonymization techniques",
                    "Conduct a Data Protection Impact Assessment (DPIA)"
                ]
            },
            {
                "id": "cross_border_transfers",
                "condition": lambda answers: answers.get("data_transfers", "") == "Yes",
                "policy": "Cross-Border Data Transfer",
                "description": "Your system transfers data across borders, requiring appropriate "
                              "transfer mechanisms.",
                "recommendations": [
                    "Implement appropriate data transfer mechanisms (SCCs, BCRs, etc.)",
                    "Assess the adequacy of data protection in recipient countries",
                    "Include appropriate contractual clauses with data recipients",
                    "Document all cross-border data transfers",
                    "Monitor changes in international data transfer regulations"
                ]
            },
            {
                "id": "data_retention",
                "condition": lambda answers: "retention_period" in answers,
                "policy": "Data Retention Policy",
                "description": "Your system should have a clear data retention policy.",
                "recommendations": [
                    lambda answers: f"Implement the stated retention period of '{answers.get('retention_period', 'undefined')}'",
                    "Create a data deletion schedule and automation if possible",
                    "Document the justification for the retention period",
                    "Implement secure data destruction methods",
                    "Regularly review and update the retention policy"
                ]
            },
            {
                "id": "access_controls",
                "condition": lambda answers: "Access Controls" in answers.get("security_measures", []),
                "policy": "Access Control Policy",
                "description": "Your system implements access controls, which should be formalized.",
                "recommendations": [
                    "Document role-based access control (RBAC) policies",
                    "Implement least privilege principles",
                    "Regularly review user access rights",
                    "Implement strong authentication methods",
                    "Create procedures for adding/removing user access"
                ]
            },
            {
                "id": "encryption",
                "condition": lambda answers: "Encryption" in answers.get("security_measures", []),
                "policy": "Encryption Policy",
                "description": "Your system uses encryption, which should be standardized across the system.",
                "recommendations": [
                    "Document encryption standards for data at rest and in transit",
                    "Implement key management procedures",
                    "Regularly update encryption algorithms to industry standards",
                    "Consider end-to-end encryption for sensitive communications",
                    "Train staff on proper encryption practices"
                ]
            },
            {
                "id": "data_processor_agreements",
                "condition": lambda answers: any(
                    answers.get(f"party_role_{party}", "") == "Data Processor"
                    for party in answers.get("data_parties", [])
                ),
                "policy": "Data Processing Agreements",
                "description": "Your system involves data processors, requiring appropriate agreements.",
                "recommendations": [
                    "Ensure Data Processing Agreements (DPAs) are in place with all processors",
                    "Include provisions for security, confidentiality, and data subject rights",
                    "Define processor obligations for data breach notification",
                    "Specify audit rights and compliance verification",
                    "Address sub-processor engagement requirements"
                ]
            },
            {
                "id": "incident_response",
                "condition": lambda answers: True,  # Always recommend incident response
                "policy": "Incident Response Plan",
                "description": "All systems should have an incident response plan for data breaches.",
                "recommendations": [
                    "Create a documented incident response procedure",
                    "Define roles and responsibilities during a breach",
                    "Establish notification timelines and procedures",
                    "Implement a process for breach severity assessment",
                    "Conduct regular incident response drills"
                ]
            }
        ]
    
    def generate_policy_suggestions(self, answers):
        """
        Generate policy suggestions based on questionnaire answers.
        
        Args:
            answers (dict): Questionnaire answers
            
        Returns:
            list: List of applicable policy suggestions
        """
        applicable_policies = []
        
        for rule in self.policy_rules:
            try:
                if rule["condition"](answers):
                    # Process recommendations - if any are lambda functions, call them with answers
                    processed_recommendations = []
                    for rec in rule["recommendations"]:
                        if callable(rec):
                            processed_recommendations.append(rec(answers))
                        else:
                            processed_recommendations.append(rec)
                    
                    applicable_policies.append({
                        "id": rule["id"],
                        "policy": rule["policy"],
                        "description": rule["description"],
                        "recommendations": processed_recommendations
                    })
            except (KeyError, TypeError, Exception) as e:
                # Skip rules that can't be evaluated due to missing data
                st.warning(f"Could not evaluate policy rule {rule['id']}: {str(e)}")
                continue
        
        return applicable_policies
    
    def render_policy_suggestions(self, answers):
        """
        Render policy suggestions in the Streamlit UI.
        
        Args:
            answers (dict): Questionnaire answers
        """
        suggestions = self.generate_policy_suggestions(answers)
        
        if not suggestions:
            st.warning("No policy suggestions could be generated. Please complete more of the questionnaire.")
            return
        
        st.write(f"Based on your responses, we recommend the following {len(suggestions)} policies:")
        
        for i, suggestion in enumerate(suggestions, 1):
            with st.expander(f"{i}. {suggestion['policy']}"):
                st.markdown(f"**Description:** {suggestion['description']}")
                st.markdown("**Recommendations:**")
                for rec in suggestion['recommendations']:
                    st.markdown(f"- {rec}")
    
    def export_policy_suggestions(self, answers, format="markdown"):
        """
        Export policy suggestions to a specific format.
        
        Args:
            answers (dict): Questionnaire answers
            format (str): Output format ("markdown", "csv", "json")
            
        Returns:
            str: Formatted policy suggestions
        """
        suggestions = self.generate_policy_suggestions(answers)
        
        if not suggestions:
            return "No policy suggestions could be generated."
        
        if format == "markdown":
            md_content = f"# Policy Suggestions for {answers.get('system_name', 'System')}\n\n"
            
            for suggestion in suggestions:
                md_content += f"## {suggestion['policy']}\n\n"
                md_content += f"{suggestion['description']}\n\n"
                md_content += "### Recommendations\n\n"
                
                for rec in suggestion['recommendations']:
                    md_content += f"- {rec}\n"
                
                md_content += "\n"
            
            return md_content
        
        elif format == "csv":
            # Flatten the suggestions for CSV format
            rows = []
            
            for suggestion in suggestions:
                for rec in suggestion['recommendations']:
                    rows.append({
                        "Policy": suggestion['policy'],
                        "Description": suggestion['description'],
                        "Recommendation": rec
                    })
            
            df = pd.DataFrame(rows)
            return df.to_csv(index=False)
        
        elif format == "json":
            import json
            return json.dumps(suggestions, indent=2)
        
        else:
            return "Unsupported export format"

# Example usage in the app:
# policy_generator = PolicyGenerator()
# policy_generator.render_policy_suggestions(st.session_state.answers)
