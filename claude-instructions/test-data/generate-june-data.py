#!/usr/bin/env python3
import json
import random
from datetime import datetime, timedelta
import os

# Base directory for test data
BASE_DIR = "/Users/stijnwillems/Developer/opens-time-chat/activitywatch-mcp/claude-instructions/test-data"

# Project names and categories
PROJECT_NAMES = [
    "ActivityWatch MCP", "TimeStory MCP", "VitalFlow MCP", "GitLab MCP Swift",
    "AW Context Tool", "DateUtil Swift", "Git MCP", "Wispr Flow Reader"
]

CATEGORIES = ["client_work", "side_project", "planning", "meeting", "break", "health"]

TAGS = [
    ["development", "swift", "mcp"], ["testing", "validation", "quality"],
    ["documentation", "api", "guides"], ["integration", "workflow", "automation"],
    ["optimization", "performance", "database"], ["architecture", "design", "patterns"],
    ["debugging", "fixes", "issues"], ["review", "feedback", "collaboration"]
]

ACHIEVEMENTS = [
    {
        "title": "MCP Protocol Enhancement",
        "descriptions": [
            "Improved protocol efficiency by optimizing JSON serialization",
            "Enhanced error handling for better user experience",
            "Implemented connection pooling for improved performance",
            "Added comprehensive logging for easier debugging"
        ]
    },
    {
        "title": "Database Optimization",
        "descriptions": [
            "Optimized query performance for large datasets",
            "Implemented efficient indexing strategies",
            "Reduced memory footprint by 30%",
            "Enhanced data integrity checks"
        ]
    },
    {
        "title": "Testing Framework",
        "descriptions": [
            "Created comprehensive test suites for all MCP tools",
            "Implemented automated integration testing",
            "Added performance benchmarking tests",
            "Established continuous testing pipeline"
        ]
    },
    {
        "title": "Documentation Update",
        "descriptions": [
            "Completed API documentation for all endpoints",
            "Created user guides and tutorials",
            "Added troubleshooting section",
            "Documented best practices and patterns"
        ]
    }
]

def generate_timesheet_data(date):
    """Generate realistic timesheet data for a given date"""
    
    # Skip weekends
    if date.weekday() >= 5:
        return None
    
    # Randomize start time between 8:00 and 9:30
    start_hour = 8 + random.choice([0, 0.25, 0.5, 0.75, 1, 1.25, 1.5])
    start_time = f"{int(start_hour):02d}:{int((start_hour % 1) * 60):02d}"
    
    # Work duration between 7.5 and 9 hours
    work_duration = random.uniform(7.5, 9)
    end_hour = start_hour + work_duration + random.uniform(0.5, 1.5)  # Add break time
    end_time = f"{int(end_hour):02d}:{int((end_hour % 1) * 60):02d}"
    
    total_minutes = int(work_duration * 60)
    break_minutes = random.randint(45, 90)
    billable_hours = round(random.uniform(4, 7), 1)
    side_project_hours = round(work_duration - billable_hours - (break_minutes / 60), 1)
    
    # Generate achievements
    num_achievements = random.randint(1, 3)
    achievements = []
    for i in range(num_achievements):
        achievement_type = random.choice(ACHIEVEMENTS)
        achievements.append({
            "type": random.choice(["primary", "secondary", "milestone"]),
            "title": achievement_type["title"],
            "description": random.choice(achievement_type["descriptions"]),
            "impact": f"Improved {random.choice(['productivity', 'reliability', 'performance', 'user experience'])} by {random.randint(15, 40)}%",
            "ticketReference": f"{random.choice(['AW', 'TS', 'MCP', 'DB'])}-{random.randint(100, 999)}"
        })
    
    # Generate timeline phases
    timeline_phases = []
    current_time = start_hour
    
    # Morning planning
    timeline_phases.append({
        "title": "Morning Planning",
        "startTime": f"{int(current_time):02d}:{int((current_time % 1) * 60):02d}",
        "endTime": f"{int(current_time + 0.5):02d}:{int(((current_time + 0.5) % 1) * 60):02d}",
        "durationMinutes": 30,
        "category": "planning",
        "description": "Daily standup and task prioritization",
        "tags": ["planning", "standup"]
    })
    current_time += 0.5
    
    # Work blocks
    while current_time < end_hour - 1:
        duration = random.uniform(1.5, 3)
        if current_time + duration > end_hour - 1:
            duration = end_hour - 1 - current_time
        
        project = random.choice(PROJECT_NAMES)
        tags = random.choice(TAGS)
        
        timeline_phases.append({
            "title": f"Work on {project}",
            "startTime": f"{int(current_time):02d}:{int((current_time % 1) * 60):02d}",
            "endTime": f"{int(current_time + duration):02d}:{int(((current_time + duration) % 1) * 60):02d}",
            "durationMinutes": int(duration * 60),
            "category": random.choice(["client_work", "side_project"]),
            "description": f"Development and testing on {project}",
            "projectName": project,
            "ticketReference": f"{project[:2].upper()}-{random.randint(100, 999)}",
            "tags": tags
        })
        current_time += duration
        
        # Add break if not near end
        if current_time < end_hour - 2 and random.random() > 0.5:
            break_duration = random.uniform(0.25, 1)
            timeline_phases.append({
                "title": "Break",
                "startTime": f"{int(current_time):02d}:{int((current_time % 1) * 60):02d}",
                "endTime": f"{int(current_time + break_duration):02d}:{int(((current_time + break_duration) % 1) * 60):02d}",
                "durationMinutes": int(break_duration * 60),
                "category": "break",
                "description": "Short break",
                "tags": ["break", "health"]
            })
            current_time += break_duration
    
    # Health metrics
    health_metrics = {
        "dataAvailable": True,
        "steps": random.randint(6000, 12000),
        "restingHeartRate": random.randint(55, 70),
        "heartRateVariability": round(random.uniform(35, 55), 1),
        "activeEnergyKj": random.randint(1800, 2800),
        "sleepDurationHours": round(random.uniform(6.5, 8.5), 1),
        "sleepQualityScore": random.randint(70, 95),
        "healthScore": random.randint(75, 95)
    }
    
    # Insights
    insights = [
        {
            "category": "productivity",
            "title": random.choice(["High Focus Day", "Productive Sprint", "Deep Work Success", "Efficient Workflow"]),
            "description": random.choice([
                "Maintained excellent focus throughout the day",
                "Completed all planned tasks ahead of schedule",
                "Achieved significant progress on key projects",
                "Optimized workflow for maximum efficiency"
            ]),
            "priority": "high"
        },
        {
            "category": "health",
            "title": random.choice(["Good Energy Levels", "Active Day", "Balanced Wellness", "Strong Recovery"]),
            "description": random.choice([
                "Physical activity supported mental performance",
                "Good sleep quality enabled sustained focus",
                "Regular breaks maintained energy levels",
                "Healthy habits contributed to productivity"
            ]),
            "priority": "medium"
        }
    ]
    
    # Metrics
    metrics = {
        "productivityScore": random.randint(75, 95),
        "focusScore": random.randint(70, 95),
        "wellnessScore": random.randint(70, 95),
        "achievementLevel": random.randint(3, 5),
        "contextSwitches": random.randint(8, 20)
    }
    
    # Git activity (some days)
    gitlab_activity = None
    if random.random() > 0.3:
        gitlab_activity = {
            "totalCommits": random.randint(3, 10),
            "totalLinesAdded": random.randint(50, 500),
            "totalLinesDeleted": random.randint(10, 100),
            "projectsWorkedOn": random.sample(PROJECT_NAMES, random.randint(1, 3)),
            "commits": []
        }
        
        for i in range(min(3, gitlab_activity["totalCommits"])):
            gitlab_activity["commits"].append({
                "hash": f"{''.join(random.choices('abcdef0123456789', k=8))}",
                "message": f"{random.choice(['feat', 'fix', 'test', 'docs'])}: {random.choice(['Add', 'Update', 'Fix', 'Improve'])} {random.choice(['feature', 'functionality', 'performance', 'documentation'])}",
                "timestamp": f"{date.strftime('%Y-%m-%d')}T{random.randint(9, 17):02d}:{random.randint(0, 59):02d}:00Z",
                "project": random.choice(gitlab_activity["projectsWorkedOn"]),
                "additions": random.randint(10, 200),
                "deletions": random.randint(5, 50)
            })
    
    data = {
        "date": date.strftime("%Y-%m-%d"),
        "timezone": "Europe/Brussels",
        "timeSummary": {
            "startTime": start_time,
            "endTime": end_time,
            "totalDurationMinutes": total_minutes,
            "billableHours": billable_hours,
            "sideProjectHours": side_project_hours,
            "breakTimeMinutes": break_minutes
        },
        "achievements": achievements,
        "timelinePhases": timeline_phases,
        "healthMetrics": health_metrics,
        "insights": insights,
        "metrics": metrics
    }
    
    if gitlab_activity:
        data["gitlabActivity"] = gitlab_activity
    
    return data

def generate_markdown_content(data):
    """Generate markdown content for the timesheet data"""
    
    date_obj = datetime.strptime(data["date"], "%Y-%m-%d")
    day_name = date_obj.strftime("%A")
    
    content = f"""# {day_name}, {date_obj.strftime('%B %d, %Y')} - Daily Activity Analysis

## 🎯 Key Achievements

"""
    
    for achievement in data["achievements"]:
        content += f"""**{achievement['title']}**
- {achievement['description']}
- {achievement['impact']}
- Reference: {achievement['ticketReference']}

"""
    
    content += f"""## ⏰ Time Distribution

**Total Work Time:** {data['timeSummary']['totalDurationMinutes'] // 60}h {data['timeSummary']['totalDurationMinutes'] % 60}m ({data['timeSummary']['totalDurationMinutes']} minutes)
- **Billable Hours:** {data['timeSummary']['billableHours']}h
- **Side Projects:** {data['timeSummary']['sideProjectHours']}h
- **Breaks:** {data['timeSummary']['breakTimeMinutes']}m

## 💡 Productivity Insights

"""
    
    for insight in data["insights"]:
        content += f"""### {insight['title']}
{insight['description']}

"""
    
    if "gitlabActivity" in data:
        content += f"""## 🚀 Development Activity

- **Commits:** {data['gitlabActivity']['totalCommits']}
- **Lines Added:** {data['gitlabActivity']['totalLinesAdded']}
- **Lines Deleted:** {data['gitlabActivity']['totalLinesDeleted']}
- **Projects:** {', '.join(data['gitlabActivity']['projectsWorkedOn'])}

"""
    
    content += f"""## 📊 Health & Performance Metrics

### Physical Health
- **Steps:** {data['healthMetrics']['steps']:,}
- **Resting Heart Rate:** {data['healthMetrics']['restingHeartRate']} bpm
- **HRV:** {data['healthMetrics']['heartRateVariability']}ms
- **Sleep Duration:** {data['healthMetrics']['sleepDurationHours']}h
- **Sleep Quality:** {data['healthMetrics']['sleepQualityScore']}%

### Performance Scores
- **Productivity:** {data['metrics']['productivityScore']}/100
- **Focus:** {data['metrics']['focusScore']}/100
- **Wellness:** {data['metrics']['wellnessScore']}/100
- **Achievement Level:** {data['metrics']['achievementLevel']}/5
- **Context Switches:** {data['metrics']['contextSwitches']}

## 🔄 Daily Workflow

"""
    
    for phase in data["timelinePhases"][:3]:  # Show first 3 phases
        content += f"""**{phase['title']}** ({phase['startTime']} - {phase['endTime']})
- {phase['description']}
- Duration: {phase['durationMinutes']} minutes
- Tags: {', '.join(phase['tags'])}

"""
    
    content += f"""---

*Generated timesheet data for {day_name}, {date_obj.strftime('%B %d, %Y')}. This day showed {'excellent' if data['metrics']['productivityScore'] > 85 else 'good' if data['metrics']['productivityScore'] > 75 else 'moderate'} productivity with a focus on {data['achievements'][0]['title'].lower()}.*"""
    
    return content

# Generate data for all days in June 2025
print("Generating test data for June 2025...")

for day in range(1, 31):
    date = datetime(2025, 6, day)
    
    # Generate data (skip weekends)
    data = generate_timesheet_data(date)
    if data:
        # Save JSON file
        json_path = os.path.join(BASE_DIR, f"2025-06-{day:02d}.json")
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Generate and save markdown file
        markdown_content = generate_markdown_content(data)
        md_path = os.path.join(BASE_DIR, f"2025-06-{day:02d}.md")
        with open(md_path, 'w') as f:
            f.write(markdown_content)
        
        print(f"✓ Generated data for {date.strftime('%Y-%m-%d')} ({date.strftime('%A')})")
    else:
        print(f"⏭️  Skipped {date.strftime('%Y-%m-%d')} ({date.strftime('%A')} - weekend)")

print("\n✅ Test data generation complete!")
print(f"📁 Files saved to: {BASE_DIR}")