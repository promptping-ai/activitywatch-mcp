#!/usr/bin/env python3
"""
Client Configuration Manager for TimeStory MCP

This tool helps users create and manage client detection rules for their time tracking.
It generates a configuration file that can be used by the ActivityWatch analysis scripts
to automatically categorize work by client.
"""

import json
import os
import sys
from datetime import datetime

class ClientConfigManager:
    def __init__(self, config_path="multi-client-config.json"):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self):
        """Load existing configuration or create default"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            return self.create_default_config()
    
    def create_default_config(self):
        """Create a default configuration template"""
        return {
            "version": "1.0.0",
            "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
            "clients": {
                "personal": {
                    "name": "Personal",
                    "displayName": "Personal/Side Projects",
                    "color": "#95E1D3",
                    "isDefault": True,
                    "detection": {
                        "folders": [],
                        "projects": [],
                        "gitlabPrefixes": [],
                        "ticketPrefixes": [],
                        "tags": ["personal", "side-project", "non-billable"]
                    }
                }
            },
            "detectionPriority": ["personal"],
            "settings": {
                "defaultClient": "personal",
                "allowMultipleClientsPerDay": True,
                "minimumBillableMinutes": 15,
                "roundBillableToNearest": 15
            }
        }
    
    def save_config(self):
        """Save configuration to file"""
        self.config["lastUpdated"] = datetime.now().strftime("%Y-%m-%d")
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        print(f"✅ Configuration saved to {self.config_path}")
    
    def add_client(self):
        """Interactive client addition"""
        print("\n🏢 Adding New Client")
        print("-" * 40)
        
        # Get client ID
        client_id = input("Client ID (lowercase, no spaces, e.g., 'acme'): ").strip().lower()
        if not client_id or client_id in self.config["clients"]:
            print("❌ Invalid or duplicate client ID")
            return
        
        # Get client details
        name = input("Client short name (e.g., 'ACME'): ").strip()
        display_name = input("Client full name (e.g., 'ACME Corporation'): ").strip()
        color = input("Client color (hex, e.g., '#FF6B6B') [optional]: ").strip() or "#4ECDC4"
        
        # Create client structure
        self.config["clients"][client_id] = {
            "name": name,
            "displayName": display_name,
            "color": color,
            "detection": {
                "folders": [],
                "projects": [],
                "gitlabPrefixes": [],
                "ticketPrefixes": [],
                "tags": []
            }
        }
        
        # Add to priority list
        if client_id not in self.config["detectionPriority"]:
            # Insert before 'personal' if it exists
            if "personal" in self.config["detectionPriority"]:
                idx = self.config["detectionPriority"].index("personal")
                self.config["detectionPriority"].insert(idx, client_id)
            else:
                self.config["detectionPriority"].append(client_id)
        
        print(f"\n✅ Client '{name}' added!")
        
        # Ask if they want to add detection rules
        if input("\nAdd detection rules now? (y/n): ").lower() == 'y':
            self.edit_client_rules(client_id)
    
    def edit_client_rules(self, client_id=None):
        """Edit detection rules for a client"""
        if not client_id:
            # List clients and let user choose
            print("\n📋 Available Clients:")
            for cid, client in self.config["clients"].items():
                if cid != "personal":  # Don't list personal as editable here
                    print(f"  - {cid}: {client['displayName']}")
            
            client_id = input("\nEnter client ID to edit: ").strip().lower()
        
        if client_id not in self.config["clients"]:
            print("❌ Client not found")
            return
        
        client = self.config["clients"][client_id]
        detection = client["detection"]
        
        print(f"\n🔧 Editing Detection Rules for {client['displayName']}")
        print("-" * 40)
        
        while True:
            print("\n1. Add folder patterns")
            print("2. Add project names")
            print("3. Add GitLab prefixes")
            print("4. Add ticket prefixes")
            print("5. Add tags")
            print("6. View current rules")
            print("7. Done")
            
            choice = input("\nChoice: ").strip()
            
            if choice == "1":
                patterns = input("Folder patterns (comma-separated, e.g., 'client-name,client-projects'): ")
                detection["folders"].extend([p.strip() for p in patterns.split(",") if p.strip()])
            
            elif choice == "2":
                projects = input("Project names (comma-separated, e.g., 'Client App,Client Dashboard'): ")
                detection["projects"].extend([p.strip() for p in projects.split(",") if p.strip()])
            
            elif choice == "3":
                prefixes = input("GitLab prefixes (comma-separated, e.g., 'client/,client-team/'): ")
                detection["gitlabPrefixes"].extend([p.strip() for p in prefixes.split(",") if p.strip()])
            
            elif choice == "4":
                prefixes = input("Ticket prefixes (comma-separated, e.g., 'CLI-,CLIENT-'): ")
                detection["ticketPrefixes"].extend([p.strip() for p in prefixes.split(",") if p.strip()])
            
            elif choice == "5":
                tags = input("Tags (comma-separated, e.g., 'client-work,billable-client'): ")
                detection["tags"].extend([t.strip() for t in tags.split(",") if t.strip()])
            
            elif choice == "6":
                print(f"\n📋 Current Rules for {client['displayName']}:")
                print(json.dumps(detection, indent=2))
            
            elif choice == "7":
                break
        
        # Remove duplicates
        for key in detection:
            if isinstance(detection[key], list):
                detection[key] = list(set(detection[key]))
        
        print(f"\n✅ Detection rules updated for {client['displayName']}")
    
    def export_instructions(self):
        """Export human-readable instructions based on config"""
        output_path = "client-work-detection-generated.md"
        
        content = f"""# Client Work Detection Instructions
Generated on {datetime.now().strftime('%Y-%m-%d')} from {self.config_path}

## Configured Clients

"""
        
        for client_id, client in self.config["clients"].items():
            if client_id == "personal":
                continue
            
            content += f"""### {client['displayName']} ({client['name']})
- **Client ID:** `{client_id}`
- **Color:** {client['color']}

#### Detection Rules:
"""
            
            detection = client["detection"]
            
            if detection.get("folders"):
                content += f"- **Folder Patterns:** {', '.join(f'`{f}`' for f in detection['folders'])}\n"
            
            if detection.get("projects"):
                content += f"- **Project Names:** {', '.join(f'`{p}`' for p in detection['projects'])}\n"
            
            if detection.get("gitlabPrefixes"):
                content += f"- **GitLab Prefixes:** {', '.join(f'`{p}`' for p in detection['gitlabPrefixes'])}\n"
            
            if detection.get("ticketPrefixes"):
                content += f"- **Ticket Prefixes:** {', '.join(f'`{p}`' for p in detection['ticketPrefixes'])}\n"
            
            if detection.get("tags"):
                content += f"- **Tags:** {', '.join(f'`{t}`' for t in detection['tags'])}\n"
            
            content += "\n"
        
        content += f"""## Settings

- **Default Client:** `{self.config['settings']['defaultClient']}`
- **Allow Multiple Clients Per Day:** {self.config['settings']['allowMultipleClientsPerDay']}
- **Minimum Billable Minutes:** {self.config['settings']['minimumBillableMinutes']}
- **Round Billable To:** {self.config['settings']['roundBillableToNearest']} minutes

## Detection Priority

Work is checked against clients in this order:
"""
        
        for i, client_id in enumerate(self.config["detectionPriority"], 1):
            client_name = self.config["clients"][client_id]["displayName"]
            content += f"{i}. {client_name}\n"
        
        with open(output_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Instructions exported to {output_path}")
    
    def run_interactive(self):
        """Run interactive configuration manager"""
        print("🎯 TimeStory Client Configuration Manager")
        print("=" * 40)
        
        while True:
            print("\n📋 Main Menu:")
            print("1. Add new client")
            print("2. Edit client detection rules")
            print("3. View current configuration")
            print("4. Export instructions (markdown)")
            print("5. Save and exit")
            print("6. Exit without saving")
            
            choice = input("\nChoice: ").strip()
            
            if choice == "1":
                self.add_client()
            
            elif choice == "2":
                self.edit_client_rules()
            
            elif choice == "3":
                print("\n📄 Current Configuration:")
                print(json.dumps(self.config, indent=2))
            
            elif choice == "4":
                self.export_instructions()
            
            elif choice == "5":
                self.save_config()
                print("👋 Goodbye!")
                break
            
            elif choice == "6":
                if input("\n⚠️  Exit without saving? (y/n): ").lower() == 'y':
                    print("👋 Goodbye!")
                    break
            
            else:
                print("❌ Invalid choice")

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "multi-client-config.json"
    
    manager = ClientConfigManager(config_path)
    
    # Check if running with command line arguments
    if len(sys.argv) > 2:
        command = sys.argv[2]
        if command == "export":
            manager.export_instructions()
        elif command == "view":
            print(json.dumps(manager.config, indent=2))
        else:
            print(f"Unknown command: {command}")
    else:
        # Run interactive mode
        manager.run_interactive()

if __name__ == "__main__":
    main()