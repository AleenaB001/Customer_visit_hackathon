import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta, timezone

from backend.config import SN_INSTANCE, SN_USERNAME, SN_PASSWORD

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

STATE_MAP = {
    "1": "New",
    "2": "In Progress",
    "3": "On Hold",
    "6": "Resolved",
    "7": "Closed"
}

PRIORITY_MAP = {
    "1": "1 - Critical",
    "2": "2 - High",
    "3": "3 - Moderate",
    "4": "4 - Low",
    "5": "5 - Planning"
}


def get_latest_incident():

    url = (
        f"{SN_INSTANCE}/api/now/table/incident"
        "?sysparm_query=ORDERBYDESCsys_created_on"
        "&sysparm_limit=1"
        "&sysparm_display_value=true"
        "&sysparm_fields="
        "number,"
        "priority,"
        "state,"
        "category,"
        "short_description,"
        "description,"
        "assignment_group,"
        "assigned_to,"
        "opened_at"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        auth=HTTPBasicAuth(SN_USERNAME, SN_PASSWORD),
        verify=False
    )

    response.raise_for_status()

    result = response.json()["result"]

    if not result:
        return None

    incident = result[0]

    return {
        "number": incident.get("number", ""),
        "priority": PRIORITY_MAP.get(
            incident.get("priority", ""),
            incident.get("priority", "")
        ),
        "state": STATE_MAP.get(
            incident.get("state", ""),
            incident.get("state", "")
        ),
        "category": incident.get("category", ""),
        "short_description": incident.get("short_description", ""),
        "description": incident.get("description", ""),
        "assignment_group": incident.get("assignment_group", ""),
        "assigned_to": incident.get("assigned_to", ""),
        "opened_at": incident.get("opened_at", "")
    }


def get_new_incidents(since_minutes: int = 1) -> list[dict]:
    """
    Fetches incidents created in the last `since_minutes` minutes
    directly from ServiceNow. Used by the notification panel.
    """
    since = datetime.now(timezone.utc) - timedelta(minutes=since_minutes)

    # ServiceNow expects: javascript:gs.dateGenerate('YYYY-MM-DD','HH:MM:SS')
    since_str = since.strftime("%Y-%m-%d %H:%M:%S")

    url = (
        f"{SN_INSTANCE}/api/now/table/incident"
        f"?sysparm_query=sys_created_on>javascript:gs.dateGenerate('{since.strftime('%Y-%m-%d')}','{since.strftime('%H:%M:%S')}')^ORDERBYDESCsys_created_on"
        "&sysparm_limit=10"
        "&sysparm_display_value=true"
        "&sysparm_fields="
        "number,"
        "priority,"
        "state,"
        "category,"
        "short_description,"
        "description,"
        "opened_at"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        auth=HTTPBasicAuth(SN_USERNAME, SN_PASSWORD),
        verify=False
    )

    response.raise_for_status()

    incidents = []

    for inc in response.json()["result"]:
        incidents.append({
            "number":            inc.get("number", ""),
            "priority":          inc.get("priority", "4 - Low"),
            "state":             inc.get("state", "New"),
            "category":          inc.get("category", ""),
            "short_description": inc.get("short_description", ""),
            "description":       inc.get("description", ""),
            "opened_at":         inc.get("opened_at", ""),
        })

    return incidents

def get_all_incidents(limit=20):

    url = (
        f"{SN_INSTANCE}/api/now/table/incident"
        f"?sysparm_limit={limit}"
        "&sysparm_query=ORDERBYDESCsys_created_on"
        "&sysparm_display_value=true"
        "&sysparm_fields="
        "number,"
        "priority,"
        "state,"
        "category,"
        "short_description,"
        "description,"
        "assignment_group,"
        "assigned_to,"
        "opened_at"          # Added here inside the string query
    )

    response = requests.get(
        url,
        headers=HEADERS,
        auth=HTTPBasicAuth(SN_USERNAME, SN_PASSWORD),
        verify=False
    )

    response.raise_for_status()

    incidents = []

    for incident in response.json()["result"]:
        incidents.append({
            "number":            incident.get("number", ""),
            "priority":          incident.get("priority", ""),
            "state":             incident.get("state", ""),
            "category":          incident.get("category", ""),
            "short_description": incident.get("short_description", ""),
            "description":       incident.get("description", ""),
            "assignment_group":  incident.get("assignment_group", ""),
            "assigned_to":       incident.get("assigned_to", ""),
            "opened_at":         incident.get("opened_at", "")   # Added here to the returned dict
        })

    return incidents
    
def get_kb_articles(limit=100):

    url = (
        f"{SN_INSTANCE}/api/now/table/kb_knowledge"
        f"?sysparm_limit={limit}"
        "&sysparm_query=workflow_state=published^numberINKB0010004,KB0010005,KB0010006,KB0010007"
        "&sysparm_display_value=true"
        "&sysparm_fields="
        "number,"
        "short_description,"
        "text"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        auth=HTTPBasicAuth(SN_USERNAME, SN_PASSWORD),
        verify=False
    )

    response.raise_for_status()

    articles = []

    for article in response.json()["result"]:
        articles.append({
            "number":            article.get("number", ""),
            "short_description": article.get("short_description", ""),
            "text":              article.get("text", "")
        })

    print(f"Articles returned: {len(articles)}")
    for article in articles:
        print(article["number"], article["short_description"])

    return articles


def get_kb_by_number(kb_number):

    url = (
        f"{SN_INSTANCE}/api/now/table/kb_knowledge"
        f"?sysparm_query=number={kb_number}"
        "&sysparm_display_value=true"
        "&sysparm_fields="
        "number,"
        "short_description,"
        "kb_description,"
        "kb_cause,"
        "kb_workaround,"
        "text"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        auth=HTTPBasicAuth(SN_USERNAME, SN_PASSWORD),
        verify=False
    )

    response.raise_for_status()

    result = response.json()["result"]

    if not result:
        return None

    return result[0]


def get_similar_incidents(incident: dict, limit: int = 5) -> list[dict]:
    """
    Finds similar incidents by same category + keyword from short_description.
    Excludes the current incident.
    """
    category = incident.get("category", "")
    current_number = incident.get("number", "")

    words = [w for w in incident.get("short_description", "").split() if len(w) > 3]
    keyword = words[0] if words else ""

    query = f"category={category}^number!={current_number}^ORDERBYDESCsys_created_on"
    if keyword:
        query += f"^short_descriptionLIKE{keyword}"

    url = (
        f"{SN_INSTANCE}/api/now/table/incident"
        f"?sysparm_query={query}"
        f"&sysparm_limit={limit}"
        "&sysparm_display_value=true"
        "&sysparm_fields=number,priority,state,category,short_description"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        auth=HTTPBasicAuth(SN_USERNAME, SN_PASSWORD),
        verify=False
    )

    response.raise_for_status()

    incidents = []
    for inc in response.json()["result"]:
        incidents.append({
            "number":            inc.get("number", ""),
            "priority":          inc.get("priority", ""),
            "state":             inc.get("state", ""),
            "category":          inc.get("category", ""),
            "short_description": inc.get("short_description", "")
        })

    return incidents

def get_resolved_incidents(limit=500):

    url = (
        f"{SN_INSTANCE}/api/now/table/incident"
        f"?sysparm_limit={limit}"
        "&sysparm_display_value=true"
        "&sysparm_query=state=6^ORstate=7"
        "&sysparm_fields="
        "number,"
        "category,"
        "priority,"
        "short_description,"
        "description,"
        "close_notes,"
        "close_code,"
        "assignment_group"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        auth=HTTPBasicAuth(SN_USERNAME, SN_PASSWORD),
        verify=False
    )

    response.raise_for_status()

    return response.json()["result"]