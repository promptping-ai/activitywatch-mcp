#!/usr/bin/env python3
import json
import os
from datetime import datetime

# Load client configuration
with open('multi-client-config.json', 'r') as f:
    CLIENT_CONFIG = json.load(f)

def detect_client_for_work(project_name, phase_data=None, gitlab_data=None):
    """Detect which client a piece of work belongs to using multi-client config"""
    
    # Check each client in priority order
    for client_id in CLIENT_CONFIG["detectionPriority"]:
        if client_id == "personal":
            continue  # Check personal last as default
        
        client = CLIENT_CONFIG["clients"][client_id]
        detection = client["detection"]
        
        # Check project name
        for pattern in detection["projects"]:
            if pattern.lower() in project_name.lower():
                return client_id
        
        # Check phase data if available
        if phase_data:
            # Check description for folder patterns
            description = phase_data.get("description", "").lower()
            for folder in detection["folders"]:
                if folder.lower() in description:
                    return client_id
            
            # Check ticket references
            ticket_ref = phase_data.get("ticketReference", "")
            for prefix in detection["ticketPrefixes"]:
                if ticket_ref.startswith(prefix):
                    return client_id
            
            # Check tags
            tags = phase_data.get("tags", [])
            if any(tag in detection["tags"] for tag in tags):
                return client_id
        
        # Check GitLab data
        if gitlab_data:
            for project in gitlab_data.get("projectsWorkedOn", []):
                if project.lower() in [p.lower() for p in detection["projects"]]:
                    return client_id
    
    # Default to personal
    return CLIENT_CONFIG["settings"]["defaultClient"]

def update_timesheet_with_multi_client(data):
    """Update timesheet data with multi-client support"""
    
    # Initialize client tracking
    client_minutes = {}
    client_projects = {}
    client_tickets = {}
    
    # Process timeline phases
    for phase in data.get("timelinePhases", []):
        if phase["category"] in ["client_work", "meeting"]:
            project_name = phase.get("projectName", "")
            client_id = detect_client_for_work(project_name, phase, data.get("gitlabActivity"))
            
            # Update phase with client ID
            phase["clientId"] = client_id
            
            # Track minutes per client
            if client_id not in client_minutes:
                client_minutes[client_id] = 0
                client_projects[client_id] = set()
                client_tickets[client_id] = set()
            
            client_minutes[client_id] += phase["durationMinutes"]
            
            if project_name:
                client_projects[client_id].add(project_name)
            
            ticket_ref = phase.get("ticketReference", "")
            if ticket_ref:
                client_tickets[client_id].add(ticket_ref)
            
            # Update category based on client
            if client_id == "personal":
                phase["category"] = "side_project"
            else:
                phase["category"] = "client_work"
    
    # Calculate hours per client
    client_hours = {}
    total_billable = 0
    side_project_hours = 0
    
    for client_id, minutes in client_minutes.items():
        hours = round(minutes / 60, 1)
        if client_id == "personal":
            side_project_hours = hours
        else:
            client_hours[client_id] = hours
            total_billable += hours
    
    # Update time summary
    data["timeSummary"]["billableHours"] = total_billable
    data["timeSummary"]["sideProjectHours"] = side_project_hours
    data["timeSummary"]["clientHours"] = client_hours if client_hours else {"personal": side_project_hours}
    
    # Create client summary
    client_summary = {}
    for client_id in client_minutes:
        if client_id != "personal" or client_minutes[client_id] > 0:
            client_summary[client_id] = {
                "hours": round(client_minutes[client_id] / 60, 1),
                "projects": list(client_projects.get(client_id, [])),
                "tickets": list(client_tickets.get(client_id, []))
            }
    
    data["clientSummary"] = client_summary
    
    # Set primary client ID
    if len(client_hours) == 0:
        data["clientId"] = "personal"
    elif len(client_hours) == 1:
        data["clientId"] = list(client_hours.keys())[0]
    else:
        data["clientId"] = "multiple"
    
    return data

def generate_multi_client_markdown(data):
    """Generate markdown with multi-client information"""
    
    date_obj = datetime.strptime(data["date"], "%Y-%m-%d")
    day_name = date_obj.strftime("%A")
    
    content = f"""# {day_name}, {date_obj.strftime('%B %d, %Y')} - Multi-Client Activity Analysis

## 🎯 Key Achievements

"""
    
    # Group achievements by client
    client_achievements = {}
    for achievement in data.get("achievements", []):
        # Detect client from achievement
        client_id = "personal"  # Default
        for phase in data.get("timelinePhases", []):
            if phase.get("ticketReference") == achievement.get("ticketReference"):
                client_id = phase.get("clientId", "personal")
                break
        
        if client_id not in client_achievements:
            client_achievements[client_id] = []
        client_achievements[client_id].append(achievement)
    
    # Write achievements by client
    for client_id, achievements in client_achievements.items():
        client_name = CLIENT_CONFIG["clients"][client_id]["displayName"]
        content += f"""### {client_name}

"""
        for achievement in achievements:
            content += f"""**{achievement['title']}**
- {achievement['description']}
- {achievement['impact']}
- Reference: {achievement['ticketReference']}

"""
    
    # Time distribution with client breakdown
    content += f"""## ⏰ Time Distribution by Client

**Total Work Time:** {data['timeSummary']['totalDurationMinutes'] // 60}h {data['timeSummary']['totalDurationMinutes'] % 60}m

### Client Breakdown
"""
    
    client_summary = data.get("clientSummary", {})
    for client_id, summary in client_summary.items():
        client_name = CLIENT_CONFIG["clients"][client_id]["displayName"]
        is_billable = client_id != "personal"
        
        content += f"""
**{client_name}:** {summary['hours']}h {"💰" if is_billable else "🚀"}
- Projects: {', '.join(summary['projects']) if summary['projects'] else 'N/A'}
- Tickets: {', '.join(summary['tickets']) if summary['tickets'] else 'N/A'}
"""
    
    content += f"""
**Total Billable:** {data['timeSummary']['billableHours']}h
**Side Projects:** {data['timeSummary']['sideProjectHours']}h
**Breaks:** {data['timeSummary']['breakTimeMinutes']}m

"""
    
    # Work phases by client
    content += """## 📊 Work Distribution

### Timeline by Client
"""
    
    # Group phases by client
    phases_by_client = {}
    for phase in data.get("timelinePhases", []):
        if phase["category"] in ["client_work", "side_project"]:
            client_id = phase.get("clientId", "personal")
            if client_id not in phases_by_client:
                phases_by_client[client_id] = []
            phases_by_client[client_id].append(phase)
    
    for client_id, phases in phases_by_client.items():
        client_name = CLIENT_CONFIG["clients"][client_id]["displayName"]
        total_minutes = sum(p["durationMinutes"] for p in phases)
        
        content += f"""
#### {client_name} ({total_minutes // 60}h {total_minutes % 60}m)
"""
        for phase in phases[:3]:  # Show top 3
            content += f"- **{phase['title']}** ({phase['startTime']}-{phase['endTime']}): {phase['durationMinutes']}m\n"
    
    # Performance metrics remain the same
    content += f"""
## 📈 Performance Metrics

| Metric | Score | Assessment |
|--------|-------|------------|
| Productivity | {data['metrics']['productivityScore']}/100 | {"Exceptional" if data['metrics']['productivityScore'] > 90 else "High" if data['metrics']['productivityScore'] > 80 else "Good"} |
| Focus Quality | {data['metrics']['focusScore']}/100 | {"Deep work" if data['metrics']['focusScore'] > 85 else "Good focus"} |
| Context Switches | {data['metrics']['contextSwitches']} | {"Excellent" if data['metrics']['contextSwitches'] < 10 else "Good" if data['metrics']['contextSwitches'] < 15 else "Moderate"} |

"""
    
    # Client-specific insights
    if len(client_summary) > 1:
        content += """## 💡 Multi-Client Insights

Working across multiple clients today:
"""
        for client_id, summary in client_summary.items():
            if summary['hours'] > 0:
                percentage = (summary['hours'] / (data['timeSummary']['totalDurationMinutes'] / 60)) * 100
                content += f"- **{CLIENT_CONFIG['clients'][client_id]['displayName']}**: {percentage:.0f}% of productive time\n"
    
    # Health metrics if available
    if "healthMetrics" in data and data["healthMetrics"]["dataAvailable"]:
        content += f"""
## 🏃 Health & Wellness

- **Steps:** {data['healthMetrics']['steps']:,}
- **Sleep Quality:** {data['healthMetrics']['sleepQualityScore']}%
- **HRV:** {data['healthMetrics']['heartRateVariability']}ms
- **Wellness Score:** {data['healthMetrics']['healthScore']}/100

"""
    
    content += f"""---

*Generated timesheet for {day_name}, {date_obj.strftime('%B %d, %Y')} with multi-client tracking enabled.*"""
    
    return content

def main():
    """Update all June timesheets with multi-client support"""
    
    print("Updating June 2025 timesheets with multi-client support...")
    print("=" * 60)
    
    # Load the manifest from previous script
    with open('june-categorization-updates.json', 'r') as f:
        manifest = json.load(f)
    
    updates = []
    
    for entry in manifest["updates"]:
        date = entry["date"]
        timesheet_id = entry["id"]
        
        # Read original JSON
        json_path = f"{date}.json"
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # Update with multi-client support
            updated_data = update_timesheet_with_multi_client(data)
            
            # Generate new markdown
            markdown_content = generate_multi_client_markdown(updated_data)
            
            # Save updated files
            with open(f"{date}-updated.json", 'w') as f:
                json.dump(updated_data, f, indent=2)
            
            with open(f"{date}-updated.md", 'w') as f:
                f.write(markdown_content)
            
            # Prepare update record
            updates.append({
                "date": date,
                "id": timesheet_id,
                "data": updated_data,
                "markdown": markdown_content
            })
            
            client_summary = updated_data.get("clientSummary", {})
            client_list = ", ".join([f"{k}: {v['hours']}h" for k, v in client_summary.items()])
            print(f"✓ Updated {date} - Clients: {client_list}")
    
    # Save update batch
    with open('june-multi-client-updates.json', 'w') as f:
        json.dump({
            "updates": [{
                "date": u["date"],
                "id": u["id"],
                "clientSummary": u["data"].get("clientSummary", {})
            } for u in updates],
            "total": len(updates)
        }, f, indent=2)
    
    print("=" * 60)
    print(f"\n✅ Updated {len(updates)} timesheets with multi-client support")
    print("\nNow use the Task tool to update TimeStory MCP with these changes")

if __name__ == "__main__":
    main()