import csv
import yaml

# Function to convert CSV to YAML inventory format
def csv_to_yaml(csv_file, yaml_file):
    inventory = {"devices": []}  # Define the structure for the inventory

    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            device = {
                "hostname": row['hostname'],
                "site": row['site'],
                "roles": row['roles'],
                "commands": row['commands'].split(";"),  # Split commands if multiple commands are separated by semicolons
                "config_commands": row['config_commands'].split(";"),
                "connection_details": {
                    "host": row['connection_details'].split(", ")[0].split(": ")[1],
                    "method": row['connection_details'].split(", ")[1].split(": ")[1],
                    "username": row['connection_details'].split(", ")[2].split(": ")[1],
                    "password": row['connection_details'].split(", ")[3].split(": ")[1]
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
