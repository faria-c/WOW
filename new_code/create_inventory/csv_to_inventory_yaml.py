import csv
import yaml

def csv_to_grouped_yaml(csv_file, yaml_file):
    inventory = {
        "networking_devices_for_vlan_changes": [],
        "http_devices": [],
        "servers": []
    }

    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            device = {
                "hostname": row['hostname'],
                "site": row['site'],
                "roles": row['roles'],
                "commands": row['commands'],
                "config_commands": row['config_commands'],
                "connection_details": {
                    "host": row['connection_details'].split(", ")[0].split(": ")[1],
                    "method": row['connection_details'].split(", ")[1].split(": ")[1],
                    "username": row['connection_details'].split(", ")[2].split(": ")[1],
                    "password": row['connection_details'].split(", ")[3].split(": ")[1]
                }
            }

            # Classify devices based on their roles and connection methods
            if "cedge" in row['roles'] or "vedge" in row['roles'] or "core" in row['roles'] or "router" in row['roles']:
                inventory["networking_devices_for_vlan_changes"].append(device)
            elif "HTTP" in row['connection_details'] or "HTTPS" in row['connection_details']:
                inventory["http_devices"].append(device)
            else:
                inventory["servers"].append(device)

    # Write the dictionary to a YAML file
    with open(yaml_file, 'w') as file:
        yaml.dump(inventory, file, default_flow_style=False)

# Example usage
csv_file = 'inventory_devices.csv'  # Input CSV file with device information
yaml_file = 'grouped_inventory.yaml'  # Output YAML file

csv_to_grouped_yaml(csv_file, yaml_file)
