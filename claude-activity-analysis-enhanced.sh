#!/bin/bash

# Enhanced ActivityWatch analysis script with client detection support
# This script uses claude-cli to analyze ActivityWatch data and generate a structured timesheet
# Now includes support for multi-client time tracking

# Default values
DATE="today"
CLIENT_CONFIG=""
CUSTOM_INSTRUCTIONS=""
OUTPUT_DIR="./analysis-output"
DEBUG=false

# Help function
show_help() {
    cat << EOF
Enhanced ActivityWatch Analysis Script with Multi-Client Support

Usage: $0 [OPTIONS]

OPTIONS:
    -d, --date DATE              Date to analyze (default: "today")
                                 Examples: "today", "yesterday", "2024-12-19"
    
    -c, --client-config FILE     Path to client detection configuration JSON
                                 (default: looks for multi-client-config.json)
    
    -i, --instructions FILE      Path to custom analysis instructions
                                 (can be combined with client config)
    
    -o, --output-dir DIR         Output directory for results (default: ./analysis-output)
    
    --debug                      Enable debug output
    
    -h, --help                   Show this help message

EXAMPLES:
    # Analyze today with client detection
    $0 --client-config ~/claude-instructions/multi-client-config.json

    # Analyze specific date with custom instructions
    $0 --date "2024-12-19" --instructions custom-rules.md

    # Analyze yesterday with both client config and custom instructions
    $0 --date yesterday -c client-config.json -i special-instructions.md

OUTPUT:
    Creates two files in the output directory:
    - {date}.json: Structured timesheet data with client breakdown
    - {date}.md: Markdown analysis with client-specific sections

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--date)
            DATE="$2"
            shift 2
            ;;
        -c|--client-config)
            CLIENT_CONFIG="$2"
            shift 2
            ;;
        -i|--instructions)
            CUSTOM_INSTRUCTIONS="$2"
            shift 2
            ;;
        -o|--output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --debug)
            DEBUG=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Build the prompt with client detection instructions
build_prompt() {
    local date=$1
    
    cat << 'EOF'
Analyze my ActivityWatch data and generate a comprehensive daily timesheet with multi-client tracking.

IMPORTANT CONTEXT:
EOF

    # Include client configuration if provided
    if [[ -n "$CLIENT_CONFIG" ]] && [[ -f "$CLIENT_CONFIG" ]]; then
        echo "=== CLIENT DETECTION CONFIGURATION ==="
        cat "$CLIENT_CONFIG"
        echo -e "\n"
    fi

    # Include custom instructions if provided
    if [[ -n "$CUSTOM_INSTRUCTIONS" ]] && [[ -f "$CUSTOM_INSTRUCTIONS" ]]; then
        echo "=== CUSTOM ANALYSIS INSTRUCTIONS ==="
        cat "$CUSTOM_INSTRUCTIONS"
        echo -e "\n"
    fi

    cat << EOF
=== ANALYSIS REQUIREMENTS ===

Please analyze my activity data for $date and create:

1. A structured JSON timesheet following this schema:
{
  "date": "YYYY-MM-DD",
  "timezone": "Europe/Brussels",
  "timeSummary": {
    "startTime": "HH:MM",
    "endTime": "HH:MM", 
    "totalDurationMinutes": number,
    "billableHours": number,  // Total across all clients
    "sideProjectHours": number,
    "breakTimeMinutes": number,
    "clientHours": {  // NEW: Hours per client
      "client_id": hours
    }
  },
  "clientSummary": {  // NEW: Summary per client
    "client_id": {
      "hours": number,
      "projects": ["project names"],
      "tickets": ["ticket references"]
    }
  },
  "achievements": [...],
  "timelinePhases": [
    {
      ...existing fields...,
      "clientId": "client_id"  // NEW: Client ID for each phase
    }
  ],
  ...rest of existing schema...
}

2. A markdown analysis that includes:
   - Client-specific sections showing work distribution
   - Clear breakdown of billable vs non-billable time
   - Insights about multi-client work patterns
   - All existing analysis elements

CRITICAL REQUIREMENTS:
- Use the client detection rules from the configuration to categorize work
- Track time separately for each client
- Identify which projects/tickets belong to which client
- Calculate billable hours per client, not just total
- Flag any ambiguous work that couldn't be clearly categorized

OUTPUT FORMAT:
First, provide the JSON data in a code block.
Then, provide the markdown analysis.

EOF
}

# Run the analysis
echo "🔍 Analyzing ActivityWatch data for $DATE..."

if [[ "$DEBUG" == true ]]; then
    echo "Debug: Using client config: $CLIENT_CONFIG"
    echo "Debug: Using custom instructions: $CUSTOM_INSTRUCTIONS"
fi

# Create temporary prompt file
PROMPT_FILE=$(mktemp)
build_prompt "$DATE" > "$PROMPT_FILE"

# Execute claude-cli with the enhanced prompt
claude_output=$(claude --model claude-3-opus-20240229 < "$PROMPT_FILE")

# Clean up temp file
rm "$PROMPT_FILE"

# Extract JSON and Markdown from the output
# This is a simplified extraction - you may need to adjust based on actual claude output format
echo "$claude_output" | awk '
    /```json/ { json=1; next }
    /```/ && json { json=0; next }
    json { json_content = json_content $0 "\n" }
    
    /```markdown/,/```/ { 
        if (!/```/) markdown_content = markdown_content $0 "\n"
    }
    
    END {
        # Find markdown content after JSON
        split($0, parts, "```")
        for (i in parts) {
            if (parts[i] ~ /^#/) {
                markdown_content = parts[i]
            }
        }
        
        print json_content > "temp_json.json"
        print markdown_content > "temp_markdown.md"
    }
'

# Determine output filenames based on date
if [[ "$DATE" == "today" ]]; then
    OUTPUT_DATE=$(date +%Y-%m-%d)
elif [[ "$DATE" == "yesterday" ]]; then
    OUTPUT_DATE=$(date -d yesterday +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)
else
    OUTPUT_DATE="$DATE"
fi

# Move files to output directory with proper names
if [[ -f "temp_json.json" ]]; then
    mv "temp_json.json" "$OUTPUT_DIR/${OUTPUT_DATE}.json"
    echo "✅ Created: $OUTPUT_DIR/${OUTPUT_DATE}.json"
fi

if [[ -f "temp_markdown.md" ]]; then
    mv "temp_markdown.md" "$OUTPUT_DIR/${OUTPUT_DATE}.md"
    echo "✅ Created: $OUTPUT_DIR/${OUTPUT_DATE}.md"
fi

# Show summary if JSON was created
if [[ -f "$OUTPUT_DIR/${OUTPUT_DATE}.json" ]]; then
    echo -e "\n📊 Summary:"
    
    # Extract client hours using jq if available
    if command -v jq &> /dev/null; then
        echo "Client breakdown:"
        jq -r '.clientSummary | to_entries[] | "  - \(.key): \(.value.hours)h"' "$OUTPUT_DIR/${OUTPUT_DATE}.json" 2>/dev/null || echo "  (Unable to parse client data)"
        
        echo -e "\nTotal billable: $(jq -r '.timeSummary.billableHours' "$OUTPUT_DIR/${OUTPUT_DATE}.json" 2>/dev/null || echo "?")h"
        echo "Side projects: $(jq -r '.timeSummary.sideProjectHours' "$OUTPUT_DIR/${OUTPUT_DATE}.json" 2>/dev/null || echo "?")h"
    fi
fi

echo -e "\n✨ Analysis complete!"