# Markdown Import Test Plan - TimeStory MCP v1.9.6

## 📋 Overview

Test the new markdown import functionality in TimeStory MCP that allows storing both structured JSON data and rich markdown analysis content together.

## 🎯 Goal

Verify that:
1. ✅ TimeStory MCP v1.9.6 is loaded correctly
2. ✅ `import_with_markdown` tool works with both JSON + markdown content
3. ✅ `get_markdown` tool retrieves stored markdown content
4. ✅ ActivityWatch workflow integration functions end-to-end

## 📁 Test Data Files

**Located in**: `claude-instructions/test-data/`

### `today.json` - Structured Timesheet Data
```json
{
  "date": "2025-06-26",
  "timezone": "Europe/Brussels",
  "timeSummary": {
    "startTime": "09:00",
    "endTime": "17:30", 
    "totalDurationMinutes": 510,
    "billableHours": 0.35,
    "sideProjectHours": 3.15
  },
  "achievements": [...],
  "timelinePhases": [...],
  "insights": [...],
  "metrics": {...}
}
```

### `today.md` - Claude Analysis Content
```markdown
## 🎯 Key Achievements

**Primary Focus: Timestory MCP Development**
- Spent 3+ hours on database schema fixes and making the system repeatable
- Major refactoring work to integrate Point-Free's sharing GRDB pattern
- Successfully made the system "repeatable by any AI"

[... full analysis content ...]
```

## 🧪 Test Procedure

### Step 1: Verify Server Version
```bash
# Expected: version "1.9.6"
mcp__timestory-mcp__get_version
```

**Expected Output:**
```json
{
  "version": "1.9.6",
  "name": "timestory-mcp", 
  "description": "TimeStory Model Context Protocol server for managing developer timesheets"
}
```

### Step 2: Check Existing Data
```bash
# Check if timesheet already exists for 2025-06-26
mcp__timestory-mcp__get_timesheet_by_date --date "2025-06-26"
```

**If exists**: Note the ID for potential cleanup
**If not exists**: Proceed to Step 2.5

### Step 2.5: Verify Database Schema
```bash
# Test if database schema supports markdown content
# Try a simple import to check for schema issues
mcp__timestory-mcp__import_with_markdown \
  --jsonData {"date":"2025-06-25","timezone":"Europe/Brussels","timeSummary":{"startTime":"09:00","endTime":"10:00","totalDurationMinutes":60}} \
  --markdownContent "Test markdown content"
```

**Expected**: Either success OR clear error about missing `markdownContent` column
**If schema error**: Database needs migration - server rebuild required
**If success**: Schema is ready - proceed to Step 3

### Step 3: Test Markdown Import
```bash
# Import with both JSON data and markdown content
mcp__timestory-mcp__import_with_markdown \
  --jsonData [JSON_CONTENT_FROM_today.json] \
  --markdownContent [MARKDOWN_CONTENT_FROM_today.md]
```

**Expected Output:**
```json
{
  "success": true,
  "id": "[UUID]",
  "message": "Timesheet with markdown content imported successfully",
  "markdownSize": [NUMBER]
}
```

### Step 4: Verify Markdown Storage
```bash
# Retrieve stored markdown content
mcp__timestory-mcp__get_markdown --date "2025-06-26"
```

**Expected Output:**
```json
{
  "success": true,
  "date": "2025-06-26",
  "timesheetId": "[UUID]",
  "markdownContent": "[FULL_MARKDOWN_CONTENT]",
  "markdownSize": [NUMBER],
  "message": "Markdown content retrieved successfully"
}
```

### Step 5: Verify Structured Data
```bash
# Check that structured data was also imported correctly
mcp__timestory-mcp__get_timestory --id "[UUID_FROM_STEP_3]"
```

**Expected**: Full timesheet data with all achievements, timeline phases, insights, etc.

## 🔧 Alternative Test Scenarios

### Scenario A: Update Existing Timesheet (If 2025-06-26 Already Exists)

1. **Delete existing**:
   ```bash
   mcp__timestory-mcp__delete_timesheet --id "[EXISTING_ID]"
   ```

2. **Import fresh with markdown**:
   ```bash
   mcp__timestory-mcp__import_with_markdown [...]
   ```

### Scenario B: Test Different Dates

```bash
# Test with yesterday's date
mcp__timestory-mcp__get_markdown --date "yesterday"

# Test with natural language
mcp__timestory-mcp__get_markdown --date "June 26"
```

## ✅ Success Criteria

- [x] **Version Check**: Server reports v1.9.6
- [x] **Tool Availability**: `import_with_markdown` and `get_markdown` tools exist
- [ ] **Database Schema**: Schema includes `markdownContent` column
- [ ] **Import Success**: JSON + markdown import completes without errors
- [ ] **Markdown Retrieval**: Stored markdown content matches input exactly
- [ ] **Data Integrity**: Structured data (achievements, phases, etc.) imported correctly
- [ ] **Natural Language**: Date parsing works with "today", "yesterday", etc.

## 🚨 Troubleshooting

### If Version Shows < 1.9.6
- Restart Claude Desktop to reload updated server
- Check timestory-mcp installation: `swift package experimental-install`

### If Tools Not Available
- Verify Claude Desktop configuration includes timestory-mcp server
- Check server logs: `~/Library/Logs/Claude/mcp-server-timestory-mcp.log`

### If Database Schema Error ("markdownContent column not found")
- Database migration required - schema doesn't support markdown import yet
- Need to rebuild timestory-mcp with updated schema
- Check if GRDB migration files include markdownContent column addition
- May need to delete existing database to force schema recreation

### If Import Fails with "Already Exists"
- Use `get_timesheet_by_date` to check existing data
- Delete existing with `delete_timesheet` if needed
- Or use `update_timesheet` to merge instead

## 📊 Expected Workflow Integration

This test validates the complete ActivityWatch → Claude → TimeStory workflow:

1. **ActivityWatch MCP** collects activity data
2. **claude-activity-analysis.sh** generates markdown analysis  
3. **convert-analysis-to-json.sh** creates structured JSON
4. **TimeStory MCP** stores both formats with `import_with_markdown`
5. **Future retrieval** preserves both structured data and rich narrative

## 🎉 Success Validation

After successful testing, the system should support:
- Rich Claude analysis preserved as markdown
- Structured data queryable for analytics
- Natural language date access to historical insights
- Complete productivity tracking workflow

---

**Test Date**: 2025-06-26  
**Expected Server Version**: 1.9.6  
**Test Files**: `claude-instructions/test-data/today.json`, `today.md`