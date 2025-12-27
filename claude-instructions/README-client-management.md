# Client Management for TimeStory MCP

This document explains how to set up and manage multi-client time tracking with TimeStory MCP.

## Overview

TimeStory MCP now supports tracking time across multiple clients with automatic detection based on:
- Folder paths
- Project names
- GitLab repositories
- Ticket prefixes
- Context tags

## Quick Start

### 1. Set Up Client Configuration

Use the interactive configuration manager:

```bash
python3 client-config-manager.py
```

This will guide you through:
- Adding new clients
- Setting up detection rules
- Configuring billing preferences

### 2. Update Your Workflow

#### When Starting Work
Add context annotations to clearly identify client work:

```bash
# For client work
echo "✳ Starting Mediahuis work - CA-5006"

# For personal projects  
echo "✳ Side project: TimeStory MCP improvements"
```

#### Folder Organization
Structure your projects for automatic detection:

```
~/Developer/
  ├── mediahuis/          # Auto-detected as Mediahuis client work
  │   ├── cueapp-ios/
  │   └── chameleon/
  ├── acme/               # Auto-detected as ACME client work
  │   └── dashboard/
  └── personal/           # Auto-detected as personal projects
      ├── timestory-mcp/
      └── activitywatch-mcp/
```

### 3. Run Analysis with Client Detection

Use the enhanced analysis script:

```bash
# Analyze with client detection
./claude-activity-analysis-enhanced.sh \
  --client-config multi-client-config.json \
  --date today

# Analyze past date
./claude-activity-analysis-enhanced.sh \
  --client-config multi-client-config.json \
  --date 2025-06-15
```

### 4. Import to TimeStory

The analysis creates JSON files with multi-client data:

```json
{
  "timeSummary": {
    "billableHours": 6.5,
    "clientHours": {
      "mediahuis": 4.5,
      "acme": 2.0
    },
    "sideProjectHours": 2.0
  },
  "clientSummary": {
    "mediahuis": {
      "hours": 4.5,
      "projects": ["CueApp iOS", "Chameleon"],
      "tickets": ["CA-5006", "CH-123"]
    }
  }
}
```

## Configuration File Format

The `multi-client-config.json` file structure:

```json
{
  "clients": {
    "client_id": {
      "name": "Short Name",
      "displayName": "Full Client Name",
      "color": "#FF6B6B",
      "detection": {
        "folders": ["client-folder", "client-projects"],
        "projects": ["Client App", "Client Dashboard"],
        "gitlabPrefixes": ["client/", "client-team/"],
        "ticketPrefixes": ["CLI-", "CLIENT-"],
        "tags": ["client-work", "billable-client"]
      }
    }
  },
  "detectionPriority": ["client1", "client2", "personal"],
  "settings": {
    "defaultClient": "personal",
    "allowMultipleClientsPerDay": true,
    "minimumBillableMinutes": 15,
    "roundBillableToNearest": 15
  }
}
```

## Detection Rules

### Priority Order

Work is categorized by checking in this order:
1. Explicit tags in context annotations
2. Ticket prefix matching
3. Project name matching
4. Folder path matching
5. GitLab repository prefixes
6. Default client (usually "personal")

### Examples

#### Folder Detection
```
~/mediahuis/cueapp-ios/  → Mediahuis client
~/acme/dashboard/        → ACME client
~/personal/mcp-tools/    → Personal project
```

#### Ticket Detection
```
"Working on CA-5006"     → Mediahuis (prefix: CA-)
"Fixed ACME-123"         → ACME (prefix: ACME-)
"Completed MCP-45"       → Personal (prefix: MCP-)
```

#### Project Detection
```
"CueApp iOS"             → Mediahuis
"ACME Dashboard"         → ACME
"TimeStory MCP"          → Personal
```

## Managing Multiple Clients

### Adding a New Client

1. Run the configuration manager:
   ```bash
   python3 client-config-manager.py
   ```

2. Choose "Add new client" and provide:
   - Client ID (lowercase, no spaces)
   - Short name
   - Full display name
   - Color (for reports)

3. Add detection rules:
   - Folder patterns
   - Project names
   - GitLab prefixes
   - Ticket prefixes
   - Tags

### Editing Detection Rules

1. Run the configuration manager
2. Choose "Edit client detection rules"
3. Select the client to edit
4. Add or modify detection patterns

### Exporting Instructions

Generate human-readable documentation:

```bash
python3 client-config-manager.py export
```

This creates `client-work-detection-generated.md` with all your current rules.

## Best Practices

### 1. Clear Folder Structure
Organize projects by client:
```
~/Developer/
  ├── [client-name]/
  │   └── [project]/
  └── personal/
      └── [project]/
```

### 2. Consistent Naming
- Use client prefixes in ticket numbers
- Include client name in project titles
- Tag commits with client identifiers

### 3. Context Annotations
Start work sessions with clear context:
```bash
# Morning start
aw-context add "Starting Mediahuis work - Sprint planning" --tags mediahuis,planning

# Task switch
aw-context add "Switching to ACME dashboard fixes" --tags acme,bugfix

# Personal project
aw-context add "Working on TimeStory MCP features" --tags personal,mcp
```

### 4. Regular Validation
Review your timesheets to ensure correct categorization:
```bash
# Check today's categorization
mcp__timestory-mcp__get_daily_summary --date today

# Review client distribution
mcp__timestory-mcp__query_timestories \
  --startDate "2025-06-01" \
  --endDate "2025-06-30"
```

## Troubleshooting

### Work Miscategorized

1. Check detection rules in config
2. Add missing patterns
3. Re-run analysis with updated config
4. Update timesheet if needed

### Missing Client Hours

1. Verify folder/project names match patterns
2. Check if context annotations include client tags
3. Review GitLab commit attribution
4. Add explicit tags if ambiguous

### Multiple Clients Not Detected

1. Ensure `allowMultipleClientsPerDay` is true
2. Check timeline phases have distinct project names
3. Verify detection patterns don't overlap
4. Use explicit context annotations for clarity

## Advanced Usage

### Custom Analysis Instructions

Combine client config with custom instructions:

```bash
./claude-activity-analysis-enhanced.sh \
  --client-config multi-client-config.json \
  --instructions special-analysis-rules.md \
  --date today
```

### Bulk Updates

Update multiple days with new client rules:

```bash
# Generate updates for a date range
for date in {1..30}; do
  ./claude-activity-analysis-enhanced.sh \
    --client-config multi-client-config.json \
    --date "2025-06-$(printf %02d $date)"
done
```

### Reporting

Generate client-specific reports:

```sql
-- Hours by client for June
SELECT 
  json_extract(client_hours, '$.' || key) as hours,
  key as client
FROM timesheets, json_each(client_hours)
WHERE date BETWEEN '2025-06-01' AND '2025-06-30'
GROUP BY client;
```

## Integration with CI/CD

Automate daily timesheet generation:

```yaml
# .github/workflows/daily-timesheet.yml
name: Generate Daily Timesheet

on:
  schedule:
    - cron: '0 18 * * 1-5'  # 6 PM on weekdays

jobs:
  generate-timesheet:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Generate timesheet
        run: |
          ./claude-activity-analysis-enhanced.sh \
            --client-config multi-client-config.json \
            --date today
      
      - name: Import to TimeStory
        run: |
          # Import logic here
```

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review your client configuration
3. Examine the analysis output logs
4. Update detection rules as needed

Remember: The goal is accurate, auditable time tracking across all your clients while maintaining clear separation between billable and personal work.