from service_now import get_latest_incident
from gemini_services import generate_resolution

incident = get_latest_incident()

print(generate_resolution(incident))