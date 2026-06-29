from backend.incident_queue import add_incident

incident = {
    "number": "INC999999",
    "priority": "4 - Low",
    "state": "New",
    "category": "Hardware",
    "short_description": "USB Queue Test",
    "description": "Testing incident notification queue"
}

add_incident(incident)

print("Incident inserted successfully.")