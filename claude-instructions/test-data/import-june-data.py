#!/usr/bin/env python3
import os
import json
import subprocess
import time
from datetime import datetime

BASE_DIR = "/Users/stijnwillems/Developer/opens-time-chat/activitywatch-mcp/claude-instructions/test-data"

def import_timesheet(date_str):
    """Import a single timesheet using MCP tool"""
    json_path = os.path.join(BASE_DIR, f"{date_str}.json")
    md_path = os.path.join(BASE_DIR, f"{date_str}.md")
    
    if not os.path.exists(json_path) or not os.path.exists(md_path):
        return None, f"Missing files for {date_str}"
    
    # Read the files
    with open(json_path, 'r') as f:
        json_data = json.load(f)
    
    with open(md_path, 'r') as f:
        markdown_content = f.read()
    
    # Import using Claude's MCP tool
    # Since we can't directly call MCP from Python, we'll prepare the data
    return {
        "date": date_str,
        "json_data": json_data,
        "markdown_content": markdown_content
    }, "Ready for import"

print("Preparing June 2025 data for import...")
print("=" * 60)

# Collect all dates to import
dates_to_import = []
import_data = []

for day in range(1, 31):
    date = datetime(2025, 6, day)
    date_str = date.strftime("%Y-%m-%d")
    
    json_path = os.path.join(BASE_DIR, f"{date_str}.json")
    md_path = os.path.join(BASE_DIR, f"{date_str}.md")
    
    if os.path.exists(json_path) and os.path.exists(md_path):
        dates_to_import.append(date_str)
        data, status = import_timesheet(date_str)
        if data:
            import_data.append(data)
            print(f"✓ Prepared {date_str} for import")
        else:
            print(f"✗ Error with {date_str}: {status}")

print("=" * 60)
print(f"\n📊 Summary:")
print(f"   - Total days to import: {len(dates_to_import)}")
print(f"   - Date range: {dates_to_import[0]} to {dates_to_import[-1]}")
print(f"\n📁 Data prepared from: {BASE_DIR}")

# Save import manifest
manifest_path = os.path.join(BASE_DIR, "june-import-manifest.json")
with open(manifest_path, 'w') as f:
    json.dump({
        "dates": dates_to_import,
        "total_days": len(dates_to_import),
        "prepared_at": datetime.now().isoformat()
    }, f, indent=2)

print(f"\n📋 Import manifest saved to: {manifest_path}")
print("\nNow use the Task tool to import each day's data using mcp__timestory-mcp__import_with_markdown")