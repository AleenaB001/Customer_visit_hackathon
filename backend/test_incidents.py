from backend.service_now import get_resolved_incidents
from backend.vector_store import incident_collection

print("=" * 80)
print("RESOLVED INCIDENTS FROM SERVICENOW")
print("=" * 80)

incidents = get_resolved_incidents()

print(f"\nTotal incidents returned: {len(incidents)}\n")

for inc in incidents:
    print(f"Number            : {inc.get('number')}")
    print(f"Short Description : {inc.get('short_description')}")
    print(f"Category          : {inc.get('category')}")
    print(f"State             : {inc.get('state')}")
    print("-" * 80)

print("\n\n")
print("=" * 80)
print("CHROMADB CONTENT")
print("=" * 80)

print(f"\nTotal vectors: {incident_collection.count()}\n")

data = incident_collection.get()

for i in range(min(10, len(data["ids"]))):

    print(f"ID: {data['ids'][i]}")
    print(f"Metadata: {data['metadatas'][i]}")
    print()

    print(data["documents"][i][:400])

    print("\n" + "=" * 80 + "\n")