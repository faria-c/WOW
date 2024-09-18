import csv
import yaml

def csv_to_yaml(csv_file, yaml_file):
    inventory = {"devices": []}

    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            device = {
                "hostname": row['hostname'],
                "management_ip": row['management_ip'],
                "connection_method": row['connection_method'],
                "credentials": {
                    "username": row['username'],
                    "password": row['password']
                }
            }
            inventory["devices"].append(device)

    with open(yaml_file, 'w') as file:
        yaml.dump(inventory, file, default_flow_style=False)

# Example usage
csv_file = 'inventory_devices.csv'
yaml_file = 'inventory.yaml'

csv_to_yaml(csv_file, yaml_file)
