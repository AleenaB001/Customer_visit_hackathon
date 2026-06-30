import os
import json
import re
import httpx
from openai import OpenAI

from backend.vector_store import search

http_client = httpx.Client(verify=False)

client = OpenAI(
    base_url="https://genailab.tcs.in",
    api_key="sk-Xnp0YZBIyM-bn3hobXm8EA",
    http_client=http_client
)


# ============================================================
# Format retrieved chunks with similarity scores
# ============================================================

def format_chunks(results):
    chunks = []

    documents = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    for doc, distance, meta in zip(documents, distances, metadatas):
        similarity = round((1 - distance) * 100, 1)
        chunks.append({
            "text":  doc,
            "score": similarity,
            "meta":  meta,
            # Flattened so UI tables (e.g. similar_incidents_card) can read
            # these directly instead of digging into "meta".
            "number":            meta.get("incident", meta.get("kb", "")),
            "category":          meta.get("category", ""),
            "priority":          meta.get("priority", ""),
            "short_description": meta.get("short_description", meta.get("title", ""))
        })

    return chunks


# ============================================================
# Generate Resolution
# ============================================================

def generate_resolution(incident):

    query = f"""
Category:
{incident['category']}

Short Description:
{incident['short_description']}

Description:
{incident['description']}
"""

    results = search(query, top_k=3)

    kb_chunks       = "\n\n".join(results["kb"]["documents"][0])
    incident_chunks = "\n\n".join(results["incidents"]["documents"][0])

    # Format BEFORE sending to LLM
    kb_formatted        = format_chunks(results["kb"])
    incident_formatted  = format_chunks(results["incidents"])

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
10. Confidence must be an integer between 0 and 100.
11. Return ONLY valid JSON.
12. Do NOT return markdown.
13. Do NOT include explanations outside the JSON.
"""

    response = client.chat.completions.create(
        model="gemini-2.5-pro",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.choices[0].message.content.strip()
    text = re.sub(r"^```json", "", text)
    text = re.sub(r"```$", "", text)
    text = text.strip()

    try:
        response_json = json.loads(text)
        response_json["retrieved_kb"]        = kb_formatted        # ✅
        response_json["retrieved_incidents"] = incident_formatted   # ✅
        return response_json

    except Exception:
        return {
            "summary":              text,
            "root_cause":           "Unknown",
            "resolution_steps":     [],
            "escalation":           "Unknown",
            "confidence":           0,
            "kb_used":              [],
            "retrieved_kb":         kb_formatted,        # ✅
            "retrieved_incidents":  incident_formatted   # ✅
        }