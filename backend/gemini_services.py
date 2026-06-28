import os
import json
import re

from google import genai

from backend.config import PROJECT_ID, LOCATION
from backend.vector_store import search


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
    BASE_DIR,
    "sa.json"
)

client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION,
)


def generate_resolution(incident):
    """
    Generates AI analysis for an incident using
    relevant KB chunks from ChromaDB.
    """

    query = f"""
Category:
{incident['category']}

Short Description:
{incident['short_description']}

Description:
{incident['description']}
"""

    # Retrieve relevant KB chunks
    results = search(query, top_k=3)

    kb_chunks = "\n\n".join(
        results["kb"]["documents"][0]
    )

    incident_chunks = "\n\n".join(
        results["incidents"]["documents"][0]
    )

    prompt = f"""
You are an expert IT Service Desk Engineer.

You have access to:

1. Official Knowledge Base Articles
2. Similar Previously Resolved Incidents

Always prioritize the Knowledge Base.
Use Similar Incidents only as supporting evidence if they align with the KB.

=================================================
CURRENT INCIDENT
=================================================

Incident Number:
{incident['number']}

Priority:
{incident['priority']}

Category:
{incident['category']}

Short Description:
{incident['short_description']}

Description:
{incident['description']}

=================================================
KNOWLEDGE BASE
=================================================

{kb_chunks}

=================================================
SIMILAR RESOLVED INCIDENTS
=================================================

{incident_chunks}

=================================================
TASK
=================================================

Analyze the incident.

Use the Knowledge Base as the primary source.

If similar incidents contain relevant resolutions,
use them only to strengthen the recommendation.

Return ONLY valid JSON.



{{
    "summary":"",
    "root_cause":"",
    "resolution_steps":[
        "action",
        "action",
        "action"
    ],
    
    "kb_used":[
        "KB0010004"
    ],
    "escalation":"Yes or No",
    "confidence":95
}}
Rules

1. Knowledge Base is the primary source of truth.
2. Similar resolved incidents are supporting evidence only.
3. Never invent troubleshooting steps.
4. Recommend only actions supported by the Knowledge Base or similar resolved incidents.
5. Preserve the troubleshooting sequence from the Knowledge Base whenever applicable.
6. Remove duplicate troubleshooting actions.
7. Return one troubleshooting action per element in resolution_steps.
8. Keep each troubleshooting action concise (maximum 2–3 sentences).
9. Populate kb_used with the KB numbers actually referenced.
10. Populate kb_used with the KB numbers actually referenced.
11. Confidence must be an integer between 0 and 100.
12. Return ONLY valid JSON.
13. Do NOT return markdown.
14. Do NOT include explanations outside the JSON.
15. Confidence must be an integer between 0 and 100.

"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    text = response.text.strip()

    # Remove markdown if Gemini returns ```json
    text = re.sub(r"^```json", "", text)
    text = re.sub(r"```$", "", text)
    text = text.strip()

    try:
        response_json = json.loads(text)

        response_json["retrieved_incidents"] = results["incidents"]

        response_json["retrieved_kb"] = results["kb"]

        return response_json

    except Exception:

        # Safe fallback
        return {
    "summary": text,
    "root_cause": "Unknown",
    "resolution_steps": [],
    "escalation": "Unknown",
    "confidence": 0,
    "kb_used": [],
    "retrieved_incidents": results["incidents"],
    "retrieved_kb": results["kb"]
}