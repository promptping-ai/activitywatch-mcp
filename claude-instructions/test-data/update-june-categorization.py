#!/usr/bin/env python3
import json
import re
from datetime import datetime

# Client work detection patterns based on client-work-detection.md
CLIENT_WORK_PATTERNS = {
    "folders": [
        "mediahuis",
        "cueapp-ios", 
        "cueappandroid",
        "chameleon",
        "frontend-chameleon",
        "mehu-",
        "-worktree-CA-",
        "-worktree-APPS-"
    ],
    "projects": [
        "Chameleon",
        "CueApp iOS",
        "CueApp Android", 
        "Sportify Swift",
        "Mediahuis"
    ],
    "gitlab_prefixes": [
        "mobile/cueapp",
        "mobile/chameleon",
        "frontend/chameleon",
        "mediahuis/"
    ]
}

SIDE_PROJECT_PATTERNS = {
    "folders": [
        "mcp",
        "activitywatch-mcp",
        "timestory-mcp",
        "vital-flow-mcp",
        "wispr-flow-mcp",
        "gitlab-mcp",
        "git-mcp",
        "opens-time-chat",
        "personal",
        "side-projects"
    ],
    "projects": [
        "ActivityWatch MCP",
        "TimeStory MCP",
        "Git MCP",
        "VitalFlow MCP",
        "GitLab MCP Swift",
        "AW Context Tool",
        "DateUtil Swift",
        "Wispr Flow Reader",
        "Swift Migration",
        "Open Source Tools",
        "Open Time Chat"
    ]
}

def is_client_work(project_name, phase_data=None):
    """Determine if work is client work based on project name and phase data"""
    
    # Check project name against client patterns
    for pattern in CLIENT_WORK_PATTERNS["projects"]:
        if pattern.lower() in project_name.lower():
            return True
    
    # Check against side project patterns (return False if found)
    for pattern in SIDE_PROJECT_PATTERNS["projects"]:
        if pattern.lower() in project_name.lower():
            return False
    
    # Check phase data if available
    if phase_data:
        # Check description for folder patterns
        description = phase_data.get("description", "").lower()
        for pattern in CLIENT_WORK_PATTERNS["folders"]:
            if pattern.lower() in description:
                return True
        
        # Check tags
        tags = phase_data.get("tags", [])
        if any(tag in ["mediahuis", "client", "billable"] for tag in tags):
            return True
    
    # Default to side project
    return False

def recalculate_hours(timeline_phases):
    """Recalculate billable and side project hours based on timeline phases"""
    
    billable_minutes = 0
    side_project_minutes = 0
    
    for phase in timeline_phases:
        if phase["category"] in ["client_work", "side_project"]:
            project_name = phase.get("projectName", "")
            
            if is_client_work(project_name, phase):
                billable_minutes += phase["durationMinutes"]
                phase["category"] = "client_work"
            else:
                side_project_minutes += phase["durationMinutes"]
                phase["category"] = "side_project"
    
    return round(billable_minutes / 60, 1), round(side_project_minutes / 60, 1)

def update_timesheet_categorization(timesheet_data):
    """Update a timesheet with proper client/side project categorization"""
    
    # Get timeline phases
    timeline_phases = timesheet_data.get("timelinePhases", [])
    
    # Recalculate hours
    billable_hours, side_project_hours = recalculate_hours(timeline_phases)
    
    # Update time summary
    timesheet_data["timeSummary"]["billableHours"] = billable_hours
    timesheet_data["timeSummary"]["sideProjectHours"] = side_project_hours
    
    # Update GitLab activity if present
    if "gitlabActivity" in timesheet_data:
        gitlab_projects = timesheet_data["gitlabActivity"].get("projectsWorkedOn", [])
        
        # Categorize projects
        client_projects = []
        side_projects = []
        
        for project in gitlab_projects:
            if is_client_work(project):
                client_projects.append(project)
            else:
                side_projects.append(project)
        
        # Update commits with correct project categorization
        for commit in timesheet_data["gitlabActivity"].get("commits", []):
            if commit.get("project"):
                # Ensure project is in correct category
                if is_client_work(commit["project"]):
                    commit["category"] = "client"
                else:
                    commit["category"] = "personal"
    
    # Add client identification
    if billable_hours > 0:
        timesheet_data["clientId"] = "mediahuis"
    else:
        timesheet_data["clientId"] = "personal"
    
    return timesheet_data

def create_update_manifest():
    """Create a manifest of all timesheets that need updating"""
    
    manifest = {
        "updates": [],
        "summary": {
            "total_days": 0,
            "client_days": 0,
            "side_project_days": 0,
            "mixed_days": 0
        }
    }
    
    # List of June dates from query
    june_dates = [
        "2025-06-02", "2025-06-03", "2025-06-04", "2025-06-05", "2025-06-06",
        "2025-06-09", "2025-06-10", "2025-06-11", "2025-06-12", "2025-06-13",
        "2025-06-16", "2025-06-17", "2025-06-18", "2025-06-19", "2025-06-20",
        "2025-06-23", "2025-06-24", "2025-06-25", "2025-06-26", "2025-06-27",
        "2025-06-30"
    ]
    
    # Timesheet IDs from the query
    timesheet_ids = {
        "2025-06-02": "38eb4664-cf90-4411-b6a2-623a0192308d",
        "2025-06-03": "35015939-5b90-4827-a3f0-0a61ccea94ae",
        "2025-06-04": "a2cda8df-2829-43af-822b-ffdd82a63a35",
        "2025-06-05": "1e8ef415-0aa7-46ed-b6ad-8aad2f18a770",
        "2025-06-06": "bdc6a499-29cb-4cf5-9994-1a9fdc71afa3",
        "2025-06-09": "b7712284-c2db-4114-9ea5-6321c682df68",
        "2025-06-10": "b6b3d9bc-cfaf-47d3-80a5-a8e5f5c0cba6",
        "2025-06-11": "719083d0-6fa7-40fe-ab81-445677331f87",
        "2025-06-12": "7f2cf43c-ef95-43cf-a98e-b42f0f31cc58",
        "2025-06-13": "b9fe0bd0-80b0-4b03-9744-eee302671252",
        "2025-06-16": "c2ffd769-41c7-45ba-8c1d-25a34c6e074d",
        "2025-06-17": "61dc19a8-e76d-4a4d-984e-4aa148712b17",
        "2025-06-18": "9702dd9d-200e-47df-8d63-ee7d524f61ac",
        "2025-06-19": "f23abbcc-ae96-4ddf-b1ec-2d16f1a98c10",
        "2025-06-20": "a8768073-96e0-4bea-b3c9-12d3a968aace",
        "2025-06-23": "adc66ad4-f338-444f-a992-73590b8183de",
        "2025-06-24": "04002219-3098-4de4-b7e1-8d2514ff81bc",
        "2025-06-25": "bf268f9c-04b4-443c-8343-6b0663bac328",
        "2025-06-26": "af44c76a-4248-4755-bd05-6445074c870a",
        "2025-06-27": "06f86db7-9c77-4eb6-9344-b875b2806d60",
        "2025-06-30": "c53ea37b-3a4c-45c7-a95a-cacd086e5296"
    }
    
    for date in june_dates:
        if date in timesheet_ids:
            # Read the original JSON file
            json_path = f"/Users/stijnwillems/Developer/opens-time-chat/activitywatch-mcp/claude-instructions/test-data/{date}.json"
            
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)
                
                # Update categorization
                updated_data = update_timesheet_categorization(data.copy())
                
                # Determine day type
                billable = updated_data["timeSummary"]["billableHours"]
                side_project = updated_data["timeSummary"]["sideProjectHours"]
                
                if billable > 0 and side_project > 0:
                    day_type = "mixed"
                    manifest["summary"]["mixed_days"] += 1
                elif billable > 0:
                    day_type = "client"
                    manifest["summary"]["client_days"] += 1
                else:
                    day_type = "side_project"
                    manifest["summary"]["side_project_days"] += 1
                
                manifest["updates"].append({
                    "date": date,
                    "id": timesheet_ids[date],
                    "day_type": day_type,
                    "billable_hours": billable,
                    "side_project_hours": side_project,
                    "updated_data": updated_data
                })
                
                manifest["summary"]["total_days"] += 1
                
                print(f"✓ Prepared update for {date} - Type: {day_type} (Client: {billable}h, Side: {side_project}h)")
                
            except Exception as e:
                print(f"✗ Error processing {date}: {e}")
    
    return manifest

def main():
    print("Analyzing June 2025 timesheets for client/side project categorization...")
    print("=" * 60)
    
    # Create update manifest
    manifest = create_update_manifest()
    
    # Save manifest
    manifest_path = "/Users/stijnwillems/Developer/opens-time-chat/activitywatch-mcp/claude-instructions/test-data/june-categorization-updates.json"
    
    # Don't save the full data in manifest, just the summary
    summary_manifest = {
        "updates": [{
            "date": u["date"],
            "id": u["id"],
            "day_type": u["day_type"],
            "billable_hours": u["billable_hours"],
            "side_project_hours": u["side_project_hours"]
        } for u in manifest["updates"]],
        "summary": manifest["summary"]
    }
    
    with open(manifest_path, 'w') as f:
        json.dump(summary_manifest, f, indent=2)
    
    print("=" * 60)
    print("\n📊 Summary:")
    print(f"   - Total days analyzed: {manifest['summary']['total_days']}")
    print(f"   - Client work days: {manifest['summary']['client_days']}")
    print(f"   - Side project days: {manifest['summary']['side_project_days']}")
    print(f"   - Mixed work days: {manifest['summary']['mixed_days']}")
    print(f"\n📋 Update manifest saved to: {manifest_path}")
    print("\nUse the Task tool to apply these updates to TimeStory MCP")

if __name__ == "__main__":
    main()