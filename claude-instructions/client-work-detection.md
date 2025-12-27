# Client Work Detection Instructions for TimeStory

## Overview
This document provides clear instructions for properly detecting and categorizing client work vs side projects in your daily timesheets. Based on your work patterns, we need to distinguish between Mediahuis client work and personal MCP development projects.

## Folder-Based Detection Rules

### Mediahuis Client Work Folders
Work in these folders should be categorized as **billable client work**:

```
~/mediahuis/
~/code/mediahuis/
~/projects/mediahuis/
/Users/*/mediahuis/

# Specific project patterns:
**/cueapp-ios/**
**/cueappandroid/**
**/chameleon/**
**/frontend-chameleon/**
**/mehu-*/**  (e.g., mehu-0002-cueapp-android)

# Work tree patterns:
**/*-worktree-CA-*/**  (e.g., android-worktree-CA-5006)
**/*-worktree-APPS-*/**
```

### Side Project Folders
Work in these folders should be categorized as **non-billable side projects**:

```
# MCP Projects
**/mcp/**
**/activitywatch-mcp/**
**/timestory-mcp/**
**/vital-flow-mcp/**
**/wispr-flow-mcp/**
**/gitlab-mcp/**
**/git-mcp/**
**/awe-context-mcp/**

# Personal Projects
**/ai-robotics/**
**/swift-date-parser/**
**/opens/**
**/personal/**
**/side-projects/**
```

## Context Annotation Tags

### Client Work Tags
Use these tags when adding context annotations for client work:
- `#mediahuis`
- `#client-work`
- `#billable`
- `#CA-[number]` (for specific tickets)
- `#APPS-[number]`

### Side Project Tags
Use these tags for personal projects:
- `#side-project`
- `#mcp`
- `#personal`
- `#non-billable`
- `#opensource`

## Terminal Context Markers

### For Client Work
```bash
# Add these markers in terminal when starting client work:
echo "✳ Starting Mediahuis work"
echo "✳ CA-5006 implementation"
echo "✳ Client: Mediahuis"
```

### For Side Projects
```bash
# Add these markers for side projects:
echo "✳ Side project: MCP development"
echo "✳ Personal: TimeStory improvements"
echo "✳ Non-billable work"
```

## GitLab Project Mapping

### Mediahuis Projects (Client Work)
GitLab projects that count as client work:
- `mobile/cueapp-ios`
- `mobile/cueappandroid`
- `mobile/chameleon`
- `mobile/frontend-chameleon`
- Any project under `mediahuis` organization

### Personal Projects (Side Projects)
- Any project under your personal GitLab namespace
- MCP-related repositories
- Open source contributions

## Practical Implementation

### 1. Morning Planning
When starting your day, explicitly declare your work type:
```javascript
// Add context annotation
add_context({
    context: "Starting Mediahuis client work - CA-5006",
    tags: ["mediahuis", "client-work", "billable"]
})
```

### 2. Folder Structure Best Practice
Organize your work to make detection automatic:
```
~/code/
  ├── mediahuis/           # All client work here
  │   ├── cueapp-ios/
  │   ├── cueappandroid/
  │   └── chameleon/
  └── personal/            # All side projects here
      ├── activitywatch-mcp/
      ├── timestory-mcp/
      └── vital-flow-mcp/
```

### 3. IDE Project Names
Configure your IDE to include client indicators in window titles:
- Xcode: "CA-5006 - Mediahuis - CueApp.xcodeproj"
- Android Studio: "Mediahuis - CueAppAndroid"
- VS Code: Add workspace names like "Mediahuis-Chameleon"

### 4. Git Commit Messages
Use clear prefixes:
```bash
# Client work commits
git commit -m "MEDIAHUIS: CA-5006 implement deep link tracking"
git commit -m "CLIENT: Fix snapshot testing for APPS-600"

# Side project commits
git commit -m "PERSONAL: Add health correlation to TimeStory"
git commit -m "MCP: Improve ActivityWatch integration"
```

## TimeStory Import Configuration

When importing timesheets, ensure proper client detection:

```javascript
// For client work entries
{
    clientId: "mediahuis",
    projectId: "cueapp-ios",
    billableHours: 5.5,
    // ... other fields
}

// For side projects
{
    clientId: "personal",
    projectId: "timestory-mcp",
    sideProjectHours: 2.0,
    // ... other fields
}
```

## Validation Checklist

Before generating your daily timesheet:

- [ ] Check if work folders contain "mediahuis" in path
- [ ] Verify GitLab commits are properly categorized
- [ ] Ensure context annotations have correct tags
- [ ] Confirm terminal markers distinguish work types
- [ ] Validate billable vs non-billable hour allocation

## Common Scenarios

### Mixed Work Sessions
When switching between client and side projects:
1. Add clear context marker when switching
2. Note the exact time of transition
3. Use terminal markers to signal the change

### Ambiguous Work
If work could benefit both client and personal projects:
- Default to client work if done during business hours
- Default to side project if it's primarily for your tools
- When in doubt, ask: "Would Mediahuis pay for this?"

## Troubleshooting

### Missing Client Work
If your timesheet shows low client hours:
1. Check if you're working in properly named folders
2. Verify ActivityWatch is capturing window titles
3. Add explicit context annotations
4. Review GitLab activity for client repositories

### Incorrectly Categorized Work
To fix miscategorized work:
1. Update folder structure to match patterns
2. Add retroactive context annotations
3. Use TimeStory update functionality to correct

---

Remember: The goal is to have clear, auditable separation between billable client work and personal development projects. When in doubt, err on the side of transparency and accurate categorization.