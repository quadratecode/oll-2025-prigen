"""
Policy suggestion module for the Data Flow Assessment tool.
Placeholder for future implementation of policy recommendations.
"""

import streamlit as st
import pandas as pd
from questions import SENSITIVE_DATA_CATEGORIES
from translations import get_text, get_formatted_text


class PolicyGenerator:
    """
    Placeholder class for generating policy suggestions based on the answers to the questionnaire.
    """

    def __init__(self):
        """Initialize the policy generator."""
        # Load policy rules and templates
        self.policy_rules = self._load_policy_rules()

    def _load_policy_rules(self):
        """
        Load simplified policy rules for the placeholder implementation.

        Returns:
            list: List of policy rule dictionaries
        """
        return [
            {
                "id": "sensitive_data",
                "condition": lambda answers: any(
                    len(answers.get(f"data_categories_{data_type}", [])) > 0
                    for data_type in answers.get("data_types", [])
                ),
                "policy": {
                    "de": "Schutz sensibler Daten",
                    "en": "Protection of Sensitive Data",
                },
                "description": {
                    "de": "Ihr System verarbeitet sensible persönliche Daten, die zusätzliche Schutzmaßnahmen erfordern.",
                    "en": "Your system processes sensitive personal data that requires additional protection measures.",
                },
                "recommendations": {
                    "de": [
                        "Implementieren Sie stärkere Sicherheitsmaßnahmen für sensible Daten",
                        "Minimieren Sie die Erfassung und Speicherung sensibler Daten",
                        "Erwägen Sie Pseudonymisierungs- oder Anonymisierungstechniken",
                    ],
                    "en": [
                        "Implement stronger security measures for sensitive data",
                        "Minimize the collection and storage of sensitive data",
                        "Consider pseudonymization or anonymization techniques",
                    ],
                },
            },
            {
                "id": "data_access",
                "condition": lambda answers: True,  # Always recommend for placeholder
                "policy": {"de": "Zugriffskontrollen", "en": "Access Controls"},
                "description": {
                    "de": "Ihr System sollte klare Zugriffskontrollen implementieren.",
                    "en": "Your system should implement clear access controls.",
                },
                "recommendations": {
                    "de": [
                        "Dokumentieren Sie Richtlinien für rollenbasierten Zugriff (RBAC)",
                        "Implementieren Sie das Prinzip der geringsten Privilegien",
                        "Überprüfen Sie regelmäßig die Zugriffsrechte der Benutzer",
                    ],
                    "en": [
                        "Document policies for role-based access control (RBAC)",
                        "Implement the principle of least privilege",
                        "Regularly review user access rights",
                    ],
                },
            },
            {
                "id": "data_retention",
                "condition": lambda answers: True,  # Always recommend for placeholder
                "policy": {
                    "de": "Datenspeicherungsrichtlinien",
                    "en": "Data Retention Policies",
                },
                "description": {
                    "de": "Ihr System sollte eine klare Datenspeicherungsrichtlinie haben.",
                    "en": "Your system should have a clear data retention policy.",
                },
                "recommendations": {
                    "de": [
                        "Legen Sie Datenspeicherungsfristen für alle Datentypen fest",
                        "Erstellen Sie einen Zeitplan für die Datenlöschung und automatisieren Sie diesen, wenn möglich",
                        "Implementieren Sie sichere Datenvernichtungsmethoden",
                    ],
                    "en": [
                        "Set data retention periods for all data types",
                        "Create a schedule for data deletion and automate it if possible",
                        "Implement secure data destruction methods",
                    ],
                },
            },
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
        language = st.session_state.get("language", "de")

        # For the placeholder, just return all policies
        for rule in self.policy_rules:
            try:
                if rule["condition"](answers):
                    applicable_policies.append(
                        {
                            "id": rule["id"],
                            "policy": rule["policy"][language],
                            "description": rule["description"][language],
                            "recommendations": rule["recommendations"][language],
                        }
                    )
            except (KeyError, TypeError, Exception) as e:
                # Skip rules that can't be evaluated due to missing data
                st.warning(f"Error evaluating policy rule {rule['id']}: {str(e)}")
                continue

        return applicable_policies

    def render_policy_suggestions(self, answers):
        """
        Render policy suggestions in the Streamlit UI.

        Args:
            answers (dict): Questionnaire answers
        """
        language = st.session_state.get("language", "de")

        # Display placeholder message
        st.info(get_text("policy_info", language))

        # Generate suggestions
        suggestions = self.generate_policy_suggestions(answers)

        if not suggestions:
            st.warning(get_text("no_policy_suggestions", language))
            return

        st.write(
            get_formatted_text(
                "policy_recommendations", language, count=len(suggestions)
            )
        )

        for i, suggestion in enumerate(suggestions, 1):
            with st.expander(f"{i}. {suggestion['policy']}"):
                st.markdown(
                    f"**{get_text('policy_description', language)}** {suggestion['description']}"
                )
                st.markdown(f"**{get_text('policy_recommendations_label', language)}**")
                for rec in suggestion["recommendations"]:
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
        language = st.session_state.get("language", "de")
        suggestions = self.generate_policy_suggestions(answers)

        if not suggestions:
            return get_text("no_policy_suggestions", language)

        if format == "markdown":
            policy_title = get_text("policy_suggestions", language)
            description_label = get_text("policy_description", language)
            recommendations_label = get_text("policy_recommendations_label", language)

            md_content = f"# {policy_title}\n\n"

            for suggestion in suggestions:
                md_content += f"## {suggestion['policy']}\n\n"
                md_content += f"{suggestion['description']}\n\n"
                md_content += f"### {recommendations_label}\n\n"

                for rec in suggestion["recommendations"]:
                    md_content += f"- {rec}\n"

                md_content += "\n"

            return md_content

        elif format == "csv":
            # Flatten the suggestions for CSV format
            rows = []
            policy_label = get_text("policy_suggestions", language)
            description_label = get_text("policy_description", language)
            recommendation_label = get_text("policy_recommendations_label", language)

            for suggestion in suggestions:
                for rec in suggestion["recommendations"]:
                    rows.append(
                        {
                            policy_label: suggestion["policy"],
                            description_label: suggestion["description"],
                            recommendation_label: rec,
                        }
                    )

            df = pd.DataFrame(rows)
            return df.to_csv(index=False)

        elif format == "json":
            import json

            return json.dumps(suggestions, indent=2)

        else:
            return "Unsupported export format"
