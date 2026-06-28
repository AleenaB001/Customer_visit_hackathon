import requests
from .config import SN_INSTANCE, SN_USERNAME, SN_PASSWORD


def get_kb_articles():
    url = f"{SN_INSTANCE}/api/now/table/kb_knowledge"

    params = {
        "sysparm_query": "workflow_state=published",
        "sysparm_limit": "1"
    }

    response = requests.get(
        url,
        auth=(SN_USERNAME, SN_PASSWORD),
        headers={"Accept": "application/json"},
        params=params
    )

    response.raise_for_status()

    return response.json()["result"]