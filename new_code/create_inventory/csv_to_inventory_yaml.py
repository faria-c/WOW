import csv
import yaml

def csv_to_grouped_yaml(csv_file, yaml_file):
    inventory = {
        "networking_devices": [],
        "http_devices": [],
        "server_devices": []
    }

    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            connection_details = row['connection_details'].split(", ")

            # Initialize default values for connection details
            host, method, username, password = "N/A", "N/A", "N/A", "N/A"

            # Parse connection details and handle missing values
            for detail in connection_details:
                if "host" in detail:
                    host = detail.split(": ")[1] if len(detail.split(": ")) > 1 else "N/A"
                elif "method" in detail:
                    method = detail.split(": ")[1] if len(detail.split(": ")) > 1 else "N/A"
                elif "username" in detail:
                    username = detail.split(": ")[1] if len(detail.split(": ")) > 1 else "N/A"
                elif "password" in detail:
                    password = detail.split(": ")[1] if len(detail.split(": ")) > 1 else "N/A"

            # Create a dictionary for the device
            device = {
                "hostname": row['hostname'],
                "site": row['site'],
                "roles": row['roles'],
                "commands": row['commands'].split(";"),
                "config_commands": row['config_commands'].split(";"),
                "connection_details": {
                    "host": host,
                    "method": method,
                    "username": username,
                    "password": password
                }
            }

            # Grouping the devices
            if "SSH" in method or "HTTPS" in method:  # Networking devices (SSH/HTTPS)
                inventory["networking_devices"].append(device)
            elif "HTTP" in method:  # HTTP devices
                inventory["http_devices"].append(device)
            else:  # Server devices (Linux, etc.)
                inventory["server_devices"].append(device)

    # Write the inventory dictionary to the YAML file
    with open(yaml_file, 'w') as file:
        yaml.dump(inventory, file, default_flow_style=False)

# Example usage
csv_file = 'inventory_sandbox_devices.csv'  # Input CSV file
yaml_file = 'grouped_inventory.yaml'  # Output YAML file

# Convert CSV to grouped YAML
csv_to_grouped_yaml(csv_file, yaml_file)
