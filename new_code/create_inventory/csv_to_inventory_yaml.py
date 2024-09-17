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
                "commands": row['commands'].split(";"),  # If multiple commands, separate by ";"
                "config_commands": row['config_commands'].split(";"),
                "connection_details": {
                    "host": row['connection_details'].split(", ")[0].split(": ")[1],
                    "auth_username": row['connection_details'].split(", ")[1].split(": ")[1],
                    "auth_password": row['connection_details'].split(", ")[2].split(": ")[1],
                    "auth_strict_key": row['connection_details'].split(", ")[3].split(": ")[1],
                    "platform": row['connection_details'].split(", ")[4].split(": ")[1]
                }
            }
            inventory["devices"].append(device)

    # Write the dictionary to a YAML file
    with open(yaml_file, 'w') as file:
        yaml.dump(inventory, file, default_flow_style=False)

# Example usage
csv_file = 'inventory_config_push.csv'  # CSV file with the device information
yaml_file = 'inventory.yaml'  # Output YAML file

csv_to_yaml(csv_file, yaml_file)
