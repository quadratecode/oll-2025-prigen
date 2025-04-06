"""
Policy suggestion module for the Data Flow Assessment tool.
Placeholder for future implementation of policy recommendations.
"""

import streamlit as st
import pandas as pd
from questions import SENSITIVE_DATA_CATEGORIES


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
                "policy": "Schutz sensibler Daten",
                "description": "Ihr System verarbeitet sensible persönliche Daten, die zusätzliche Schutzmaßnahmen erfordern.",
                "recommendations": [
                    "Implementieren Sie stärkere Sicherheitsmaßnahmen für sensible Daten",
                    "Minimieren Sie die Erfassung und Speicherung sensibler Daten",
                    "Erwägen Sie Pseudonymisierungs- oder Anonymisierungstechniken",
                ],
            },
            {
                "id": "data_access",
                "condition": lambda answers: True,  # Always recommend for placeholder
                "policy": "Zugriffskontrollen",
                "description": "Ihr System sollte klare Zugriffskontrollen implementieren.",
                "recommendations": [
                    "Dokumentieren Sie Richtlinien für rollenbasierten Zugriff (RBAC)",
                    "Implementieren Sie das Prinzip der geringsten Privilegien",
                    "Überprüfen Sie regelmäßig die Zugriffsrechte der Benutzer",
                ],
            },
            {
                "id": "data_retention",
                "condition": lambda answers: True,  # Always recommend for placeholder
                "policy": "Datenspeicherungsrichtlinien",
                "description": "Ihr System sollte eine klare Datenspeicherungsrichtlinie haben.",
                "recommendations": [
                    "Legen Sie Datenspeicherungsfristen für alle Datentypen fest",
                    "Erstellen Sie einen Zeitplan für die Datenlöschung und automatisieren Sie diesen, wenn möglich",
                    "Implementieren Sie sichere Datenvernichtungsmethoden",
                ],
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

        # For the placeholder, just return all policies
        for rule in self.policy_rules:
            try:
                if rule["condition"](answers):
                    applicable_policies.append(
                        {
                            "id": rule["id"],
                            "policy": rule["policy"],
                            "description": rule["description"],
                            "recommendations": rule["recommendations"],
                        }
                    )
            except (KeyError, TypeError, Exception) as e:
                # Skip rules that can't be evaluated due to missing data
                st.warning(
                    f"Fehler bei der Auswertung der Richtlinienregel {rule['id']}: {str(e)}"
                )
                continue

        return applicable_policies

    def render_policy_suggestions(self, answers):
        """
        Render policy suggestions in the Streamlit UI.

        Args:
            answers (dict): Questionnaire answers
        """
        # Display placeholder message
        st.info(
            "Dies ist ein Platzhalter für die Richtlinienvorschlagsfunktion. In zukünftigen Versionen werden hier automatisch generierte Richtlinienvorschläge angezeigt."
        )

        # Generate suggestions
        suggestions = self.generate_policy_suggestions(answers)

        if not suggestions:
            st.warning(
                "Es konnten keine Richtlinienvorschläge generiert werden. Bitte vervollständigen Sie mehr Fragen im Fragebogen."
            )
            return

        st.write(
            f"Basierend auf Ihren Antworten empfehlen wir die folgenden {len(suggestions)} Richtlinien:"
        )

        for i, suggestion in enumerate(suggestions, 1):
            with st.expander(f"{i}. {suggestion['policy']}"):
                st.markdown(f"**Beschreibung:** {suggestion['description']}")
                st.markdown("**Empfehlungen:**")
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
        suggestions = self.generate_policy_suggestions(answers)

        if not suggestions:
            return "Es konnten keine Richtlinienvorschläge generiert werden."

        if format == "markdown":
            md_content = f"# Richtlinienvorschläge\n\n"

            for suggestion in suggestions:
                md_content += f"## {suggestion['policy']}\n\n"
                md_content += f"{suggestion['description']}\n\n"
                md_content += "### Empfehlungen\n\n"

                for rec in suggestion["recommendations"]:
                    md_content += f"- {rec}\n"

                md_content += "\n"

            return md_content

        elif format == "csv":
            # Flatten the suggestions for CSV format
            rows = []

            for suggestion in suggestions:
                for rec in suggestion["recommendations"]:
                    rows.append(
                        {
                            "Richtlinie": suggestion["policy"],
                            "Beschreibung": suggestion["description"],
                            "Empfehlung": rec,
                        }
                    )

            df = pd.DataFrame(rows)
            return df.to_csv(index=False)

        elif format == "json":
            import json

            return json.dumps(suggestions, indent=2)

        else:
            return "Nicht unterstütztes Exportformat"
