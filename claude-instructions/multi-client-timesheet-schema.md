# Multi-Client Timesheet Schema Enhancement

## Current Schema Limitations

The current TimeStory schema has:
- Single `billableHours` field (total for all clients)
- Single `sideProjectHours` field
- Single `clientId` field

This doesn't support tracking hours across multiple clients in a single day.

## Proposed Schema Enhancements

### Option 1: Client Hours Map (Recommended)

Add a `clientHours` object that maps client IDs to hours:

```json
{
  "date": "2025-06-26",
  "timeSummary": {
    "startTime": "09:00",
    "endTime": "17:30",
    "totalDurationMinutes": 510,
    "billableHours": 6.5,  // Keep for backward compatibility (sum of all clients)
    "sideProjectHours": 2.0,
    "clientHours": {
      "mediahuis": 4.5,
      "acme": 2.0
    }
  }
}
```

### Option 2: Enhanced Timeline Phases

Add `clientId` to each timeline phase:

```json
{
  "timelinePhases": [
    {
      "title": "CueApp iOS Development",
      "category": "client_work",
      "clientId": "mediahuis",  // NEW FIELD
      "projectName": "CueApp iOS",
      "durationMinutes": 150
    },
    {
      "title": "ACME Dashboard Features", 
      "category": "client_work",
      "clientId": "acme",  // NEW FIELD
      "projectName": "ACME Dashboard",
      "durationMinutes": 120
    }
  ]
}
```

### Option 3: Comprehensive Solution (Best)

Combine both approaches for maximum flexibility:

```json
{
  "timeSummary": {
    "billableHours": 6.5,  // Total (backward compatible)
    "clientHours": {       // Breakdown by client
      "mediahuis": 4.5,
      "acme": 2.0
    },
    "sideProjectHours": 2.0
  },
  "timelinePhases": [
    {
      "clientId": "mediahuis",  // Track at phase level
      "billable": true,
      "hourlyRate": 150  // Optional: for invoicing
    }
  ],
  "clientSummary": {  // NEW: Daily client summary
    "mediahuis": {
      "hours": 4.5,
      "projects": ["CueApp iOS", "Chameleon"],
      "tickets": ["CA-5006", "CH-123"],
      "commits": 3
    },
    "acme": {
      "hours": 2.0,
      "projects": ["ACME Dashboard"],
      "tickets": ["ACME-456"],
      "commits": 1
    }
  }
}
```

## Implementation Strategy

### 1. Database Migration

```sql
-- Add client tracking columns
ALTER TABLE timesheets ADD COLUMN client_hours JSON;
ALTER TABLE timesheets ADD COLUMN client_summary JSON;

-- Update timeline_phases table
ALTER TABLE timeline_phases ADD COLUMN client_id TEXT;
ALTER TABLE timeline_phases ADD COLUMN billable BOOLEAN DEFAULT false;
```

### 2. Detection Algorithm

```python
def detect_client_for_phase(phase, client_config):
    """
    Detect which client a work phase belongs to
    Priority order:
    1. Explicit client tag in context
    2. Ticket prefix matching
    3. Project name matching
    4. Folder path matching
    5. Default client
    """
    
    # Check each client's detection rules
    for client_id in client_config["detectionPriority"]:
        client = client_config["clients"][client_id]
        
        # Check various detection methods
        if matches_client_patterns(phase, client["detection"]):
            return client_id
    
    return client_config["settings"]["defaultClient"]
```

### 3. Time Allocation Algorithm

```python
def allocate_client_hours(timeline_phases, client_config):
    """
    Allocate hours to different clients based on timeline phases
    """
    client_minutes = {}
    
    for phase in timeline_phases:
        if phase["category"] in ["client_work", "meeting"]:
            client_id = detect_client_for_phase(phase, client_config)
            
            if client_id not in client_minutes:
                client_minutes[client_id] = 0
            
            client_minutes[client_id] += phase["durationMinutes"]
    
    # Convert to hours and round as configured
    client_hours = {}
    round_to = client_config["settings"]["roundBillableToNearest"]
    
    for client_id, minutes in client_minutes.items():
        if minutes >= client_config["settings"]["minimumBillableMinutes"]:
            # Round to nearest configured interval
            rounded_minutes = round(minutes / round_to) * round_to
            client_hours[client_id] = round(rounded_minutes / 60, 2)
    
    return client_hours
```

## Usage Examples

### 1. Single Client Day (Backward Compatible)

```json
{
  "clientId": "mediahuis",  // Keep for compatibility
  "billableHours": 7.5,
  "clientHours": {
    "mediahuis": 7.5
  }
}
```

### 2. Multi-Client Day

```json
{
  "clientId": "multiple",  // Special indicator
  "billableHours": 7.5,    // Total
  "clientHours": {
    "mediahuis": 5.0,
    "acme": 2.5
  }
}
```

### 3. Mixed Client and Personal Day

```json
{
  "billableHours": 5.0,
  "sideProjectHours": 3.0,
  "clientHours": {
    "mediahuis": 3.0,
    "acme": 2.0
  }
}
```

## Reporting Enhancements

### 1. Client-Specific Reports

```sql
-- Hours by client for a period
SELECT 
  client_id,
  SUM(hours) as total_hours,
  COUNT(DISTINCT date) as days_worked
FROM (
  SELECT 
    date,
    json_each.key as client_id,
    json_each.value as hours
  FROM timesheets, json_each(client_hours)
  WHERE date BETWEEN ? AND ?
)
GROUP BY client_id;
```

### 2. Project Distribution by Client

```sql
-- Project hours by client
SELECT 
  tp.client_id,
  tp.project_name,
  SUM(tp.duration_minutes) / 60.0 as hours
FROM timeline_phases tp
JOIN timesheets t ON t.id = tp.timesheet_id
WHERE t.date BETWEEN ? AND ?
GROUP BY tp.client_id, tp.project_name;
```

## Migration Path

1. **Phase 1**: Add `clientHours` to timeSummary (backward compatible)
2. **Phase 2**: Add `clientId` to timeline phases
3. **Phase 3**: Implement client detection algorithm
4. **Phase 4**: Add `clientSummary` for rich reporting
5. **Phase 5**: Update UI/reports to use multi-client data

## Benefits

1. **Accurate Billing**: Track exact hours per client
2. **Better Insights**: See work distribution across clients
3. **Flexible Detection**: Automatic client detection with manual override
4. **Backward Compatible**: Existing single-client data still works
5. **Extensible**: Easy to add new clients via configuration