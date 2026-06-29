import json
import random
from datetime import datetime, timedelta

def generate_synthetic_data():
    current_time = datetime.now()
    incidents = []
    
    # 1. Define exact operational mappings derived from KB parameters
    kb_mappings = {
        "🏦 Payment Gateway": {
            "causes": ["DB Pool Exhaustion", "API Timeout", "Network Latency"],
            "titles": ["Payment Gateway – DB Pool Exhaustion", "Transaction Processing Timeout", "Gateway Gateway Latency Spike"]
        },
        "🔐 Identity Service": {
            "causes": ["Certificate Expired", "LDAP Failure", "Time drift on authenticator app"],
            "titles": ["SSO Login Failure - SAML token invalid", "Mass Active Directory Account Lockout", "MFA Token Mismatch Validation Loop"]
        },
        "🌐 API Gateway": {
            "causes": ["API Timeout", "Network Latency", "Cache Overflow"],
            "titles": ["Edge Gateway Timeout", "Network Route Latency Spike", "Redis Cluster Cache Overflow"]
        },
        "👤 Customer Portal": {
            "causes": ["Cache Overflow", "Memory Leak", "Password Expired"],
            "titles": ["Session Storage Cache Overflow", "Portal Dashboard Memory Leak", "SSPR Portal Redirection Sync Failure"]
        },
        "🔔 Notification Service": {
            "causes": ["Memory Leak", "API Timeout"],
            "titles": ["Worker Queue Memory Leak", "SMS Gateway HTTP Timeout"]
        },
        "🗄 Database Service": {
            "causes": ["Disk Space Full", "DB Pool Exhaustion"],
            "titles": ["Production Instance Disk Space Full", "Connection Pool Exhaustion Alert"]
        }
    }
    
    apps = list(kb_mappings.keys())
    priorities = ["P1", "P2", "P3", "P4"]
    
    # --- STEP A: GENERATE HISTORICAL RESOLVED DATA (Weeks 1 to 14) ---
    # We target roughly 165 historical items to reach our dashboard total target safely
    incident_counter = 1001
    
    for week_offset in range(14):
        # Scale incident volume slightly upwards across weeks to match the 'trending up' UI visual
        weekly_volume = random.randint(8 + week_offset, 12 + week_offset)
        
        for _ in range(weekly_volume):
            app = random.choice(apps)
            priority = random.choices(priorities, weights=[0.1, 0.25, 0.45, 0.2])[0]
            cause = random.choice(kb_mappings[app]["causes"])
            title = random.choice(kb_mappings[app]["titles"])
            
            # Distribute backwards over time
            days_back = (13 - week_offset) * 7 + random.randint(0, 6)
            hours_back = random.randint(1, 23)
            created_date = current_time - timedelta(days=days_back, hours=hours_back)
            
            # Calculate MTTR targets ensuring a ~78% AI approval baseline
            # P1s resolve faster, P3/P4 can sit longer
            if priority == "P1":
                mttr = random.randint(20, 75)
            elif priority == "P2":
                mttr = random.randint(120, 300)
            else:
                mttr = random.randint(300, 1600)
                
            resolved_date = created_date + timedelta(minutes=mttr)
            
            # Track feedback compliance matching dashboard constraints
            ai_worked = random.random() < 0.78
            feedback = "Resolution Worked" if ai_worked else "Incorrect Recommendation"
            confidence = round(random.uniform(0.65, 0.95), 2)
            
            incidents.append({
                "incident_id": f"INC{incident_counter}",
                "title": title,
                "application": app,
                "priority": priority,
                "status": "Resolved" if random.random() < 0.8 else "Closed",
                "root_cause": cause,
                "mttr_minutes": mttr,
                "created_date": created_date.isoformat(),
                "resolved_date": resolved_date.isoformat(),
                "ai_resolution": {
                    "confidence_score": confidence,
                    "root_cause_predicted": cause if ai_worked else random.choice(kb_mappings[app]["causes"])
                },
                "feedback": feedback
            })
            incident_counter += 1

    # --- STEP B: INJECT EXPLICIT REAL-TIME ACTIVE INCIDENTS ---
    # To keep your UI strictly coherent with the mockup data: 5 Active P1s, 3 of which breach SLA
    live_p1_scenarios = [
        {"id": "INC1042", "app": "🏦 Payment Gateway", "title": "Payment Gateway – DB Pool Exhaustion", "age_mins": 78}, # Breached (SLA 60)
        {"id": "INC1156", "app": "🔐 Identity Service", "title": "Identity Service – Certificate Expired", "age_mins": 34},
        {"id": "INC1178", "app": "🌐 API Gateway", "title": "API Gateway – Network Latency Spike", "age_mins": 22},
        {"id": "INC1181", "app": "👤 Customer Portal", "title": "Customer Portal – Cache Overflow", "age_mins": 11},
        {"id": "INC1184", "app": "🗄 Database Service", "title": "Database Service – Disk Space Full", "age_mins": 4}
    ]
    
    for p1 in live_p1_scenarios:
        created_dt = current_time - timedelta(minutes=p1["age_mins"])
        incidents.append({
            "incident_id": p1["id"],
            "title": p1["title"],
            "application": p1["app"],
            "priority": "P1",
            "status": "In Progress" if p1["age_mins"] > 30 else "Open",
            "root_cause": None,
            "mttr_minutes": None,
            "created_date": created_dt.isoformat(),
            "resolved_date": None,
            "ai_resolution": {
                "confidence_score": round(random.uniform(0.70, 0.90), 2),
                "root_cause_predicted": "DB Pool Exhaustion" if "DB" in p1["title"] else "Anomaly Detected"
            },
            "feedback": None
        })
        
    # Other dynamic open lower-priority items to fill dashboard metrics cleanly
    for age_hours, priority, app, title in [(5, "P2", "🔐 Identity Service", "Customer Portal – LDAP Failure"), 
                                            (27, "P3", "🔔 Notification Service", "Notification Service – Memory Leak")]:
        created_dt = current_time - timedelta(hours=age_hours, minutes=12 if age_hours==5 else 40)
        incidents.append({
            "incident_id": f"INC{incident_counter}",
            "title": title,
            "application": app,
            "priority": priority,
            "status": "Open",
            "root_cause": None,
            "mttr_minutes": None,
            "created_date": created_dt.isoformat(),
            "resolved_date": None,
            "ai_resolution": None,
            "feedback": None
        })
        incident_counter += 1

    # Save output dataset
    with open("raw_incidents.json", "w") as f:
        json.dump(incidents, f, indent=4)
    print(f"Successfully generated {len(incidents)} raw incident stream records inside raw_incidents.json!")

if __name__ == "__main__":
    generate_synthetic_data()