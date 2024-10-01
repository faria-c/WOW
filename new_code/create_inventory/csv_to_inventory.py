import csv
import yaml

# Function to create inventory.yaml from CSV data
def create_inventory_from_csv(csv_file, yaml_file):
    inventory = {'networking_devices_for_vlan_changes': []}

    with open(csv_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            device = {
                'site': row['Site Name'],
                'hostname': row['Device Name'],
                'device_type': row['Device Type'],
                'connection_details': {
                    'host': row['Device Name'],
                    'username': row['Username'],
                    'password': row['Password'],
                    'method': 'SSH' if row['Device Type'] != 'vManage' else 'HTTPS',
                }
            }
            if row['Device Type'] == 'SD-WAN Device':
                device['sd_wan_var'] = row['sd-wan var']
                device['sd_wan_var_value'] = row['sd-wan var value']

            inventory['networking_devices_for_vlan_changes'].append(device)

    # Write inventory.yaml
    with open(yaml_file, 'w') as yamlfile:
        yaml.dump(inventory, yamlfile, default_flow_style=False)

# Example usage
csv_file = 'device_inventory.csv'  # Replace with the path to your CSV file
yaml_file = 'inventory.yaml'  # The output YAML file
create_inventory_from_csv(csv_file, yaml_file)
