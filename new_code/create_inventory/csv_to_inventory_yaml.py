import csv
import yaml
import os

def csv_to_grouped_yaml(csv_file, yaml_file):
    inventory = {
        "networking_devices_for_vlan_changes": [],
        "http_devices": [],
        "servers": []
    }

    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Safely split connection_details and initialize with "N/A" if any detail is missing
            connection_details = row['connection_details'].split(", ")
            host = method = username = password = "N/A"

            for detail in connection_details:
                if "host" in detail:
                    host = detail.split(": ")[1] if len(detail.split(": ")) > 1 else "N/A"
                elif "method" in detail:
                    method = detail.split(": ")[1] if len(detail.split(": ")) > 1 else "N/A"
                elif "username" in detail:
                    username = detail.split(": ")[1] if len(detail.split(": ")) > 1 else "N/A"
                elif "password" in detail:
                    password = detail.split(": ")[1] if len(detail.split(": ")) > 1 else "N/A"

            # Create device dictionary
            device = {
                "hostname": row['hostname'],
                "site": row['site'],
                "roles": row['roles'],
                "commands": row['commands'],
                "config_commands": row['config_commands'],
                "connection_details": {
                    "host": host,
                    "method": method,
                    "username": username,
                    "password": password
                }
            }

            # Classify devices into groups
            if "cedge" in row['roles'] or "vedge" in row['roles'] or "core" in row['roles'] or "router" in row['roles']:
                inventory["networking_devices_for_vlan_changes"].append(device)
            elif "HTTP" in row['connection_details'] or "HTTPS" in row['connection_details']:
                inventory["http_devices"].append(device)
            else:
                inventory["servers"].append(device)

    # Create output directory if not existing
    if not os.path.exists('yaml_output'):
        os.makedirs('yaml_output')

    # Write inventory to YAML file inside 'yaml_output' directory
    with open(os.path.join('yaml_output', yaml_file), 'w') as file:
        yaml.dump(inventory, file, default_flow_style=False)

# Example usage
csv_file = 'inventory_devices.csv'  # Input CSV file with device information
yaml_file = 'inventory.yaml'  # Output YAML file

csv_to_grouped_yaml(csv_file, yaml_file)
