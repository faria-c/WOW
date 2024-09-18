import csv
import yaml

def csv_to_yaml(csv_file, yaml_file):
    inventory = {"devices": []}

    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Parse connection details field
            connection_details = row['connection_details'].split(", ")

            # Initialize default values
            host, method, username, password = "N/A", "N/A", "N/A", "N/A"

            # Parse each detail
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
                "management_ip": host,
                "connection_method": method,
                "credentials": {
                    "username": username,
                    "password": password
                }
            }

            inventory["devices"].append(device)

    # Write inventory to YAML file
    with open(yaml_file, 'w') as file:
        yaml.dump(inventory, file, default_flow_style=False)

# Example usage
csv_file = 'inventory_devices.csv'
yaml_file = 'inventory.yaml'

csv_to_yaml(csv_file, yaml_file)
