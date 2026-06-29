import json
import os
import http.server
import socketserver
import webbrowser
from datetime import datetime

PORT = 8080

def preprocess_and_serve():
    if not os.path.exists("raw_incidents.json"):
        print("Error: raw_incidents.json missing! Please run generate_data.py first.")
        return

    with open("raw_incidents.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    current_time = datetime.now()
    sla_thresholds = {"P1": 60, "P2": 240, "P3": 1440, "P4": 2880}

    # Preprocessing Storage Arrays & Metrics
    total_count = len(raw_data)
    open_count = 0
    resolved_count = 0
    total_mttr = 0
    sla_compliant_count = 0
    
    active_sla_breaches_list = []
    open_p1_list = []
    
    app_aggregations = {}
    priority_counts = {"P1": 0, "P2": 0, "P3": 0, "P4": 0}
    root_cause_counts = {}
    
    weeks_list = [f"W{i}" for i in range(1, 15)]
    weekly_volume_trends = {w: {"new": 0, "resolved": 0} for w in weeks_list}
    weekly_mttr_sums = {w: {"total_mttr": 0, "count": 0, "p1_mttr": 0, "p1_count": 0} for w in weeks_list}
    
    # FIX: Use consistent 14-week array length across all trend datasets
    feedback_weekly = {w: {"Worked": 0, "Failed": 0} for w in weeks_list}
    ai_root_cause_perf = {}
    
    total_resolutions_generated = 0
    confidence_score_sum = 0
    feedback_worked_count = 0
    feedback_total_count = 0

    # Stream Processing Loop
    for inc in raw_data:
        created_dt = datetime.fromisoformat(inc["created_date"])
        priority = inc["priority"]
        app = inc["application"]
        status = inc["status"]
        
        priority_counts[priority] += 1
        
        if app not in app_aggregations:
            app_aggregations[app] = {
                "open": 0, "active_p1": 0, "total_mttr": 0, 
                "resolved_count": 0, "sla_compliant": 0, 
                "history_count": 0, "root_causes": {}
            }
        
        days_old = (current_time - created_dt).days
        week_idx = 14 - (days_old // 7)
        week_key = f"W{max(1, min(14, week_idx))}"
        
        weekly_volume_trends[week_key]["new"] += 1

        # Real-time Ticket Routing State Machine
        if status in ["Open", "In Progress"]:
            open_count += 1
            app_aggregations[app]["open"] += 1
            
            age_minutes = int((current_time - created_dt).total_seconds() / 60)
            threshold = sla_thresholds[priority]
            
            if age_minutes > threshold:
                active_sla_breaches_list.append({
                    "id": inc["incident_id"],
                    "age_str": f"{age_minutes} min" if age_minutes < 60 else f"{age_minutes//60}h {age_minutes%60}m",
                    "title": inc["title"]
                })
                
            if priority == "P1":
                open_p1_list.append({
                    "id": inc["incident_id"],
                    "title": inc["title"],
                    "app": app,
                    "age_mins": age_minutes
                })
                app_aggregations[app]["active_p1"] += 1
                
        elif status in ["Resolved", "Closed"]:
            resolved_count += 1
            app_aggregations[app]["resolved_count"] += 1
            weekly_volume_trends[week_key]["resolved"] += 1
            
            mttr = inc["mttr_minutes"]
            total_mttr += mttr
            app_aggregations[app]["total_mttr"] += mttr
            
            weekly_mttr_sums[week_key]["total_mttr"] += mttr
            weekly_mttr_sums[week_key]["count"] += 1
            
            if priority == "P1":
                weekly_mttr_sums[week_key]["p1_mttr"] += mttr
                weekly_mttr_sums[week_key]["p1_count"] += 1
            
            if mttr < sla_thresholds[priority]:
                sla_compliant_count += 1
                app_aggregations[app]["sla_compliant"] += 1
                
            rc = inc["root_cause"]
            if rc:
                root_cause_counts[rc] = root_cause_counts.get(rc, 0) + 1
                app_aggregations[app]["root_causes"][rc] = app_aggregations[app]["root_causes"].get(rc, 0) + 1

        # Model Performance Sub-aggregations
        if inc.get("ai_resolution") and inc["ai_resolution"] is not None:
            total_resolutions_generated += 1
            confidence_score_sum += inc["ai_resolution"]["confidence_score"]
            
        fb = inc.get("feedback")
        if fb:
            feedback_total_count += 1
            rc = inc["root_cause"]
            if rc not in ai_root_cause_perf:
                ai_root_cause_perf[rc] = {"worked": 0, "total": 0}
            ai_root_cause_perf[rc]["total"] += 1
            
            if week_key in feedback_weekly:
                if fb == "Resolution Worked":
                    feedback_worked_count += 1
                    feedback_weekly[week_key]["Worked"] += 1
                    ai_root_cause_perf[rc]["worked"] += 1
                else:
                    feedback_weekly[week_key]["Failed"] += 1

    # Format Output Metrics & Trends arrays
    processed_volume_new = [weekly_volume_trends[w]["new"] for w in weeks_list]
    processed_volume_res = [weekly_volume_trends[w]["resolved"] for w in weeks_list]
    processed_mttr_avg = [int(weekly_mttr_sums[w]["total_mttr"] / max(1, weekly_mttr_sums[w]["count"])) for w in weeks_list]
    processed_mttr_p1 = [int(weekly_mttr_sums[w]["p1_mttr"] / max(1, weekly_mttr_sums[w]["p1_count"])) for w in weeks_list]

    # Calculate Root Cause Lists
    sorted_rc = sorted(root_cause_counts.items(), key=lambda x: x[1], reverse=True)
    root_causes_payload = [{"cause": k, "count": v, "pct": round((v / max(1, resolved_count)) * 100, 1)} for k, v in sorted_rc]

    # Build Application Scorecard UI Payload with Health Derived Logic
    scorecard_payload = []
    for app_name, metrics in app_aggregations.items():
        app_resolved = metrics["resolved_count"]
        app_sla = int((metrics["sla_compliant"] * 100) / max(1, app_resolved)) if app_resolved > 0 else 100
        active_p1 = metrics["active_p1"]
        
        highest_rc_count = max(metrics["root_causes"].values()) if metrics["root_causes"] else 0
        recurrence_rate = int((highest_rc_count * 100) / max(1, app_resolved)) if app_resolved > 0 else 0
        
        if active_p1 > 0 and app_sla < 80:
            health = "Critical"
        elif active_p1 > 0 or app_sla < 90:
            health = "Degraded"
        else:
            health = "Healthy"
            
        scorecard_payload.append({
            "name": app_name,
            "health": health,
            "open": metrics["open"],
            "active_p1": active_p1,
            "avg_mttr": int(metrics["total_mttr"] / max(1, app_resolved)) if app_resolved > 0 else 0,
            "sla": app_sla,
            "recurrence": recurrence_rate
        })

    # AI Accuracy by Root Cause
    ai_rc_rows = []
    for rc, values in ai_root_cause_perf.items():
        pct = int((values["worked"] * 100) / max(1, values["total"]))
        ai_rc_rows.append({"cause": rc, "pct": pct})
    ai_rc_rows = sorted(ai_rc_rows, key=lambda x: x["pct"], reverse=True)

    # Compile Unified Payload Object
    live_payload = {
        "kpis": {
            "total": total_count,
            "open": open_count,
            "resolved": resolved_count,
            "avg_mttr": int(total_mttr / max(1, resolved_count)) if resolved_count > 0 else 0,
            "sla_compliance": int((sla_compliant_count * 100) / max(1, resolved_count)) if resolved_count > 0 else 100,
            "ai_approval": int((feedback_worked_count * 100) / max(1, feedback_total_count)) if feedback_total_count > 0 else 0
        },
        "active_breaches": active_sla_breaches_list,
        "open_p1s": open_p1_list,
        "volume_weeks": weeks_list,
        "volume_new": processed_volume_new,
        "volume_resolved": processed_volume_res,
        "by_app_labels": list(app_aggregations.keys()),
        "by_app_values": [app_aggregations[a]["open"] + app_aggregations[a]["resolved_count"] for a in app_aggregations.keys()],
        "by_priority": [priority_counts["P1"], priority_counts["P2"], priority_counts["P3"], priority_counts["P4"]],
        "root_causes": root_causes_payload,
        "scorecard": scorecard_payload,
        "mttr_overall": processed_mttr_avg,
        "mttr_p1": processed_mttr_p1,
        "feedback_weeks": weeks_list,
        "feedback_worked": [feedback_weekly[w]["Worked"] for w in weeks_list],
        "feedback_failed": [feedback_weekly[w]["Failed"] for w in weeks_list],
        "ai_stats": {
            "approval": int((feedback_worked_count * 100) / max(1, feedback_total_count)) if feedback_total_count > 0 else 0,
            "confidence": round(confidence_score_sum / max(1, total_resolutions_generated), 2) if total_resolutions_generated > 0 else 0.0,
            "incorrect": 100 - (int((feedback_worked_count * 100) / max(1, feedback_total_count)) if feedback_total_count > 0 else 0),
            "total_generated": total_resolutions_generated
        },
        "ai_rc_perf": ai_rc_rows
    }

    if not os.path.exists("dashboard_demo.html"):
        print("Error: dashboard_demo.html not found.")
        return
        
    with open("dashboard_demo.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    # FIX: Direct object literal replacement for cleaner JS injection
    html_content = html_content.replace('/*%%LIVE_DATA%%*/', json.dumps(live_payload))

    with open("live_dashboard_runtime.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    class LocalDashboardHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/" or self.path == "/index.html":
                self.path = "/live_dashboard_runtime.html"
            return super().do_GET()

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), LocalDashboardHandler) as httpd:
        print(f"🌍 Live Dashboard active at http://localhost:{PORT}")
        webbrowser.open(f"http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down dashboard server components.")

if __name__ == "__main__":
    preprocess_and_serve()