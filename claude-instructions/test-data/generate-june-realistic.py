#!/usr/bin/env python3
import json
import random
from datetime import datetime, timedelta
import os

# Base directory for test data
BASE_DIR = "/Users/stijnwillems/Developer/opens-time-chat/activitywatch-mcp/claude-instructions/test-data"

# Git activity from analysis
GIT_ACTIVITY_DATES = {
    "2025-06-17": {
        "commits": 7,
        "projects": ["ActivityWatch MCP", "Swift Migration"],
        "focus": "Swift implementation and documentation"
    },
    "2025-06-19": {
        "commits": 6,
        "projects": ["ActivityWatch MCP", "DateUtil Swift"],
        "focus": "Natural language date parsing and bug fixes"
    },
    "2025-06-26": {
        "commits": 9,
        "projects": ["ActivityWatch MCP", "TimeStory MCP", "Claude Integration"],
        "focus": "Claude integration and workflow optimization"
    }
}

# Projects based on folder activity
ACTIVE_PROJECTS = {
    "opens-time-chat": ["ActivityWatch MCP", "TimeStory MCP", "Git MCP", "VitalFlow MCP"],
    "gitlab-mcp": ["GitLab MCP Swift", "MCP Protocol"],
    "mediahuis": ["Chameleon", "CueApp iOS", "CueApp Android", "Sportify Swift"],
    "web": ["Vimeo Integration", "Apple Developer", "GitHub Projects"]
}

# Realistic work patterns
WORK_PATTERNS = {
    "deep_work": {
        "duration": (2.5, 4),
        "focus_score": (85, 95),
        "context_switches": (4, 8)
    },
    "meetings": {
        "duration": (0.5, 1.5),
        "focus_score": (60, 75),
        "context_switches": (15, 25)
    },
    "debugging": {
        "duration": (1, 2.5),
        "focus_score": (75, 85),
        "context_switches": (10, 18)
    },
    "documentation": {
        "duration": (1, 2),
        "focus_score": (80, 90),
        "context_switches": (6, 12)
    }
}

def get_project_for_date(date):
    """Get realistic projects based on date and git activity"""
    date_str = date.strftime("%Y-%m-%d")
    
    if date_str in GIT_ACTIVITY_DATES:
        return GIT_ACTIVITY_DATES[date_str]["projects"]
    
    # Assign projects based on week patterns
    week_num = date.isocalendar()[1]
    if week_num % 2 == 0:
        return ["Chameleon", "CueApp iOS", "Sportify Swift"]
    else:
        return ["ActivityWatch MCP", "TimeStory MCP", "Git MCP"]

def generate_realistic_timeline(date, projects):
    """Generate timeline based on actual work patterns"""
    timeline = []
    
    # Determine work pattern for the day
    day_patterns = []
    if date.weekday() == 0:  # Monday - planning heavy
        day_patterns = ["meetings", "deep_work", "documentation"]
    elif date.weekday() == 4:  # Friday - wrap up
        day_patterns = ["deep_work", "documentation", "meetings"]
    else:  # Tue-Thu - productive days
        day_patterns = ["deep_work", "debugging", "deep_work"]
    
    # Generate start time (based on real patterns)
    start_hour = random.choice([8.5, 8.75, 9.0, 9.25])
    current_time = start_hour
    
    # Morning standup
    timeline.append({
        "title": "Morning Standup & Planning",
        "startTime": f"{int(current_time):02d}:{int((current_time % 1) * 60):02d}",
        "endTime": f"{int(current_time + 0.5):02d}:{int(((current_time + 0.5) % 1) * 60):02d}",
        "durationMinutes": 30,
        "category": "meeting",
        "description": "Daily sync with team and priority setting",
        "tags": ["meeting", "planning", "team"]
    })
    current_time += 0.5
    
    # Work blocks based on patterns
    for i, pattern in enumerate(day_patterns):
        work_info = WORK_PATTERNS[pattern]
        duration = random.uniform(*work_info["duration"])
        
        project = random.choice(projects)
        
        if pattern == "deep_work":
            title = f"Development: {project}"
            category = "client_work" if project in ["Chameleon", "CueApp iOS"] else "side_project"
            description = f"Feature development and implementation on {project}"
            tags = ["development", "coding", "feature"]
        elif pattern == "debugging":
            title = f"Debugging & Testing: {project}"
            category = "client_work"
            description = f"Investigating issues and implementing fixes for {project}"
            tags = ["debugging", "testing", "fixes"]
        elif pattern == "documentation":
            title = f"Documentation: {project}"
            category = "side_project"
            description = f"API documentation and usage guides for {project}"
            tags = ["documentation", "writing", "api"]
        else:  # meetings
            title = "Team Meeting / Code Review"
            category = "meeting"
            description = "Collaborative session with team"
            tags = ["meeting", "review", "collaboration"]
        
        timeline.append({
            "title": title,
            "startTime": f"{int(current_time):02d}:{int((current_time % 1) * 60):02d}",
            "endTime": f"{int(current_time + duration):02d}:{int(((current_time + duration) % 1) * 60):02d}",
            "durationMinutes": int(duration * 60),
            "category": category,
            "description": description,
            "projectName": project,
            "tags": tags
        })
        current_time += duration
        
        # Add lunch break after morning session
        if i == 0 and current_time < 14:
            lunch_duration = random.uniform(0.75, 1.25)
            timeline.append({
                "title": "Lunch Break",
                "startTime": f"{int(current_time):02d}:{int((current_time % 1) * 60):02d}",
                "endTime": f"{int(current_time + lunch_duration):02d}:{int(((current_time + lunch_duration) % 1) * 60):02d}",
                "durationMinutes": int(lunch_duration * 60),
                "category": "break",
                "description": "Lunch and walk" if random.random() > 0.5 else "Lunch break",
                "tags": ["break", "lunch", "health"]
            })
            current_time += lunch_duration
        
        # Add short breaks
        elif i < len(day_patterns) - 1 and random.random() > 0.4:
            break_duration = random.uniform(0.15, 0.25)
            timeline.append({
                "title": "Short Break",
                "startTime": f"{int(current_time):02d}:{int((current_time % 1) * 60):02d}",
                "endTime": f"{int(current_time + break_duration):02d}:{int(((current_time + break_duration) % 1) * 60):02d}",
                "durationMinutes": int(break_duration * 60),
                "category": "break",
                "description": "Quick break",
                "tags": ["break", "health"]
            })
            current_time += break_duration
    
    return timeline, start_hour, current_time

def generate_git_activity(date, projects):
    """Generate git activity based on actual patterns"""
    date_str = date.strftime("%Y-%m-%d")
    
    if date_str in GIT_ACTIVITY_DATES:
        # Use actual data
        git_data = GIT_ACTIVITY_DATES[date_str]
        commits = []
        
        for i in range(git_data["commits"]):
            commit_type = random.choice(['feat', 'fix', 'refactor', 'docs', 'test'])
            action = random.choice(['Add', 'Update', 'Fix', 'Improve', 'Implement'])
            feature = random.choice(['MCP integration', 'error handling', 'performance', 'documentation', 'testing'])
            
            commits.append({
                "hash": ''.join(random.choices('abcdef0123456789', k=8)),
                "message": f"{commit_type}: {action} {feature}",
                "timestamp": f"{date_str}T{random.randint(9, 17):02d}:{random.randint(0, 59):02d}:00Z",
                "project": random.choice(git_data["projects"]),
                "additions": random.randint(20, 200),
                "deletions": random.randint(5, 50)
            })
        
        return {
            "totalCommits": git_data["commits"],
            "totalLinesAdded": sum(c["additions"] for c in commits),
            "totalLinesDeleted": sum(c["deletions"] for c in commits),
            "projectsWorkedOn": git_data["projects"],
            "commits": commits[:3]  # Show top 3
        }
    
    # Generate typical activity for other days
    if random.random() > 0.4:  # 60% chance of git activity
        num_commits = random.randint(2, 6)
        commits = []
        
        for i in range(min(3, num_commits)):
            commits.append({
                "hash": ''.join(random.choices('abcdef0123456789', k=8)),
                "message": f"{random.choice(['feat', 'fix'])}: {random.choice(['Update', 'Add', 'Fix'])} {random.choice(['feature', 'bug', 'test'])}",
                "timestamp": f"{date_str}T{random.randint(9, 17):02d}:{random.randint(0, 59):02d}:00Z",
                "project": random.choice(projects),
                "additions": random.randint(10, 150),
                "deletions": random.randint(5, 40)
            })
        
        return {
            "totalCommits": num_commits,
            "totalLinesAdded": sum(c["additions"] for c in commits) + random.randint(0, 100),
            "totalLinesDeleted": sum(c["deletions"] for c in commits) + random.randint(0, 30),
            "projectsWorkedOn": list(set(c["project"] for c in commits)),
            "commits": commits
        }
    
    return None

def generate_realistic_health_metrics(date, work_duration):
    """Generate health metrics correlated with work patterns"""
    # Higher activity on days with git commits
    date_str = date.strftime("%Y-%m-%d")
    is_high_activity = date_str in GIT_ACTIVITY_DATES
    
    base_steps = 8000 if is_high_activity else 7000
    steps = random.randint(base_steps - 2000, base_steps + 3000)
    
    # Better sleep before productive days
    sleep_quality = random.randint(75, 90) if is_high_activity else random.randint(70, 85)
    sleep_duration = round(random.uniform(7, 8) if sleep_quality > 80 else random.uniform(6.5, 7.5), 1)
    
    # HRV correlates with recovery
    hrv = round(random.uniform(42, 52) if sleep_quality > 80 else random.uniform(38, 45), 1)
    
    return {
        "dataAvailable": True,
        "steps": steps,
        "restingHeartRate": random.randint(58, 68),
        "heartRateVariability": hrv,
        "activeEnergyKj": int(steps * 0.25) + random.randint(-200, 200),
        "sleepDurationHours": sleep_duration,
        "sleepQualityScore": sleep_quality,
        "healthScore": int((sleep_quality + (steps/100) + hrv) / 3)
    }

def generate_realistic_timesheet(date):
    """Generate realistic timesheet data based on actual patterns"""
    
    # Skip weekends
    if date.weekday() >= 5:
        return None
    
    # Get projects for this date
    projects = get_project_for_date(date)
    
    # Generate timeline
    timeline, start_hour, end_hour = generate_realistic_timeline(date, projects)
    
    # Calculate totals
    total_minutes = int((end_hour - start_hour) * 60)
    work_phases = [p for p in timeline if p["category"] in ["client_work", "side_project"]]
    break_phases = [p for p in timeline if p["category"] == "break"]
    
    work_minutes = sum(p["durationMinutes"] for p in work_phases)
    break_minutes = sum(p["durationMinutes"] for p in break_phases)
    
    client_minutes = sum(p["durationMinutes"] for p in work_phases if p["category"] == "client_work")
    side_minutes = sum(p["durationMinutes"] for p in work_phases if p["category"] == "side_project")
    
    # Generate achievements based on git activity
    date_str = date.strftime("%Y-%m-%d")
    achievements = []
    
    if date_str in GIT_ACTIVITY_DATES:
        git_info = GIT_ACTIVITY_DATES[date_str]
        achievements.append({
            "type": "primary",
            "title": f"{git_info['focus']}",
            "description": f"Significant progress on {', '.join(git_info['projects'])}",
            "impact": "Major feature implementation and improvements",
            "ticketReference": f"GIT-{date.day:02d}"
        })
    
    # Add regular achievements
    achievements.extend([{
        "type": random.choice(["secondary", "primary"]),
        "title": f"Progress on {random.choice(projects)}",
        "description": f"Completed {random.choice(['feature implementation', 'bug fixes', 'performance optimization', 'code review'])}",
        "impact": f"Improved {random.choice(['reliability', 'performance', 'user experience', 'code quality'])}",
        "ticketReference": f"{projects[0][:2].upper()}-{random.randint(100, 999)}"
    }])
    
    # Generate health metrics
    health_metrics = generate_realistic_health_metrics(date, work_minutes / 60)
    
    # Generate git activity
    git_activity = generate_git_activity(date, projects)
    
    # Calculate scores based on actual patterns
    focus_score = 90 if date_str in GIT_ACTIVITY_DATES else random.randint(75, 88)
    context_switches = random.randint(8, 15) if focus_score > 85 else random.randint(12, 20)
    
    data = {
        "date": date.strftime("%Y-%m-%d"),
        "timezone": "Europe/Brussels",
        "timeSummary": {
            "startTime": f"{int(start_hour):02d}:{int((start_hour % 1) * 60):02d}",
            "endTime": f"{int(end_hour):02d}:{int((end_hour % 1) * 60):02d}",
            "totalDurationMinutes": total_minutes,
            "billableHours": round(client_minutes / 60, 1),
            "sideProjectHours": round(side_minutes / 60, 1),
            "breakTimeMinutes": break_minutes
        },
        "achievements": achievements,
        "timelinePhases": timeline,
        "healthMetrics": health_metrics,
        "insights": [
            {
                "category": "productivity",
                "title": "Development Focus" if focus_score > 85 else "Steady Progress",
                "description": f"{'High-impact development day' if date_str in GIT_ACTIVITY_DATES else 'Consistent progress on ongoing projects'}",
                "priority": "high"
            },
            {
                "category": "health",
                "title": "Work-Life Balance",
                "description": f"{'Good recovery and energy levels' if health_metrics['sleepQualityScore'] > 80 else 'Adequate rest for productivity'}",
                "priority": "medium"
            }
        ],
        "metrics": {
            "productivityScore": focus_score + random.randint(-5, 5),
            "focusScore": focus_score,
            "wellnessScore": health_metrics["healthScore"],
            "achievementLevel": 5 if date_str in GIT_ACTIVITY_DATES else random.randint(3, 4),
            "contextSwitches": context_switches
        }
    }
    
    if git_activity:
        data["gitlabActivity"] = git_activity
    
    return data

def generate_realistic_markdown(data):
    """Generate markdown content with realistic analysis"""
    
    date_obj = datetime.strptime(data["date"], "%Y-%m-%d")
    day_name = date_obj.strftime("%A")
    date_str = data["date"]
    
    # Determine if this was a high-activity day
    is_highlight_day = date_str in GIT_ACTIVITY_DATES
    
    content = f"""# {day_name}, {date_obj.strftime('%B %d, %Y')} - Daily Activity Analysis

## 🎯 Key Achievements

"""
    
    for achievement in data["achievements"]:
        content += f"""**{achievement['title']}**
- {achievement['description']}
- {achievement['impact']}
- Reference: {achievement['ticketReference']}

"""
    
    if is_highlight_day:
        git_info = GIT_ACTIVITY_DATES[date_str]
        content += f"""### 🚀 High-Impact Development Day
Today marked significant progress with **{git_info['commits']} commits** focused on {git_info['focus']}. 
The concentrated effort on {', '.join(git_info['projects'])} demonstrates deep technical work and meaningful feature advancement.

"""
    
    content += f"""## ⏰ Time Distribution

**Total Work Time:** {data['timeSummary']['totalDurationMinutes'] // 60}h {data['timeSummary']['totalDurationMinutes'] % 60}m
- **Client Work:** {data['timeSummary']['billableHours']}h
- **Side Projects:** {data['timeSummary']['sideProjectHours']}h  
- **Breaks:** {data['timeSummary']['breakTimeMinutes']}m

### Work Pattern Analysis
"""
    
    # Analyze work patterns
    work_phases = [p for p in data["timelinePhases"] if p["category"] in ["client_work", "side_project"]]
    longest_focus = max(work_phases, key=lambda x: x["durationMinutes"])
    
    content += f"""**Longest Focus Block:** {longest_focus['durationMinutes']} minutes on {longest_focus.get('projectName', 'project work')}
**Context Switches:** {data['metrics']['contextSwitches']} ({"excellent" if data['metrics']['contextSwitches'] < 10 else "good" if data['metrics']['contextSwitches'] < 15 else "moderate"})
**Peak Productivity:** {longest_focus['startTime']} - {longest_focus['endTime']}

"""
    
    if "gitlabActivity" in data:
        content += f"""## 💻 Development Activity

### Git Statistics
- **Total Commits:** {data['gitlabActivity']['totalCommits']}
- **Lines Added:** {data['gitlabActivity']['totalLinesAdded']:,}
- **Lines Deleted:** {data['gitlabActivity']['totalLinesDeleted']:,}
- **Net Change:** +{data['gitlabActivity']['totalLinesAdded'] - data['gitlabActivity']['totalLinesDeleted']:,} lines
- **Projects:** {', '.join(data['gitlabActivity']['projectsWorkedOn'])}

### Key Commits
"""
        for commit in data['gitlabActivity']['commits']:
            content += f"- `{commit['hash'][:7]}` - {commit['message']} (+{commit['additions']}/-{commit['deletions']})\n"
        
        content += "\n"
    
    content += f"""## 📊 Health & Wellness

### Physical Activity
- **Steps:** {data['healthMetrics']['steps']:,} {"🏃" if data['healthMetrics']['steps'] > 10000 else ""}
- **Active Energy:** {data['healthMetrics']['activeEnergyKj']:,} kJ
- **Movement Pattern:** {"High activity" if data['healthMetrics']['steps'] > 9000 else "Moderate activity" if data['healthMetrics']['steps'] > 7000 else "Low activity"}

### Recovery Metrics  
- **Sleep Duration:** {data['healthMetrics']['sleepDurationHours']}h
- **Sleep Quality:** {data['healthMetrics']['sleepQualityScore']}%
- **HRV:** {data['healthMetrics']['heartRateVariability']}ms
- **Resting HR:** {data['healthMetrics']['restingHeartRate']} bpm

### Wellness Score: {data['healthMetrics']['healthScore']}/100
{"Excellent recovery and energy levels" if data['healthMetrics']['healthScore'] > 85 else "Good overall wellness" if data['healthMetrics']['healthScore'] > 75 else "Adequate wellness levels"}

## 🎯 Performance Analysis

| Metric | Score | Assessment |
|--------|-------|------------|
| Productivity | {data['metrics']['productivityScore']}/100 | {"Exceptional" if data['metrics']['productivityScore'] > 90 else "High" if data['metrics']['productivityScore'] > 80 else "Good"} |
| Focus Quality | {data['metrics']['focusScore']}/100 | {"Deep work achieved" if data['metrics']['focusScore'] > 85 else "Good concentration" if data['metrics']['focusScore'] > 75 else "Moderate focus"} |
| Achievement | {data['metrics']['achievementLevel']}/5 | {"Major milestones" if data['metrics']['achievementLevel'] == 5 else "Solid progress" if data['metrics']['achievementLevel'] >= 4 else "Steady advancement"} |

## 💡 Daily Insights

"""
    
    for insight in data["insights"]:
        content += f"""### {insight['title']}
{insight['description']}

"""
    
    # Add correlation analysis
    if data['healthMetrics']['sleepQualityScore'] > 80 and data['metrics']['productivityScore'] > 85:
        content += """### 🔄 Positive Correlation
Today demonstrates the clear link between quality rest and high productivity. The combination of good sleep 
({data['healthMetrics']['sleepQualityScore']}%) and focused work blocks resulted in exceptional output.

"""
    
    content += f"""---

*Analysis for {day_name}, {date_obj.strftime('%B %d, %Y')}. """
    
    if is_highlight_day:
        content += "This was a standout day with significant technical achievements and excellent work-life balance.*"
    else:
        content += "A productive day maintaining consistent progress across multiple projects.*"
    
    return content

# Generate data for all days in June 2025
print("Generating realistic test data for June 2025 based on actual activity patterns...")
print("=" * 60)

generated_count = 0
skipped_count = 0

for day in range(1, 31):
    date = datetime(2025, 6, day)
    
    # Skip days that already have data
    json_path = os.path.join(BASE_DIR, f"2025-06-{day:02d}.json")
    if os.path.exists(json_path):
        print(f"⏭️  Skipping {date.strftime('%Y-%m-%d')} - already exists")
        skipped_count += 1
        continue
    
    # Generate data (skip weekends)
    data = generate_realistic_timesheet(date)
    if data:
        # Save JSON file
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Generate and save markdown file
        markdown_content = generate_realistic_markdown(data)
        md_path = os.path.join(BASE_DIR, f"2025-06-{day:02d}.md")
        with open(md_path, 'w') as f:
            f.write(markdown_content)
        
        is_git_day = date.strftime("%Y-%m-%d") in GIT_ACTIVITY_DATES
        print(f"✓ Generated {date.strftime('%Y-%m-%d')} ({date.strftime('%A')}) {'🚀 HIGH ACTIVITY' if is_git_day else ''}")
        generated_count += 1
    else:
        print(f"⏭️  Skipped {date.strftime('%Y-%m-%d')} ({date.strftime('%A')} - weekend)")
        skipped_count += 1

print("=" * 60)
print(f"\n✅ Generation complete!")
print(f"📊 Summary:")
print(f"   - Generated: {generated_count} days")
print(f"   - Skipped: {skipped_count} days (weekends + existing)")
print(f"   - Total work days: {generated_count}")
print(f"\n📁 Files saved to: {BASE_DIR}")