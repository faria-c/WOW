import csv
import yaml

# Function to convert CSV to YAML inventory format
def csv_to_yaml(csv_file, yaml_file):
    inventory = {"devices": []}  # Define the structure for the inventory

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

            # Build device entry
            device = {
                "hostname": row['hostname'],
                "site": row['site'],
                "roles": row['roles'],
                "commands": row['commands'].split(";"),  # Split commands if multiple commands are separated by semicolons
                "config_commands": row['config_commands'].split(";"),
                "connection_details": {
                    "host": host,
                    "method": method,
                    "username": username,
                    "password": password
                }
            }
            inventory["devices"].append(device)

    # Write the dictionary to a YAML file
    with open(yaml_file, 'w') as file:
        yaml.dump(inventory, file, default_flow_style=False)

# Example usage
csv_file = 'inventory_sandbox_devices.csv'  # Input CSV file with device information
yaml_file = 'inventory.yaml'  # Output YAML file

# Convert the CSV to YAML
csv_to_yaml(csv_file, yaml_file)
