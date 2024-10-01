import csv
import yaml

# Function to create inventory.yaml from CSV data
def create_inventory_from_csv(csv_file, yaml_file):
    inventory = {'networking_devices_for_vlan_changes': []}

    with open(csv_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            # Split method(s) by comma and take the first method
            methods = row['Method(s)'].split(',')  # Split by comma
            primary_method = methods[0].strip()  # Take the first method and strip any extra spaces

            # Create the device entry with proper field mappings
            device = {
                'site': row['Site Name'],
                'hostname': row['Device Name'],
                'device_type': row['Device Type'],
                'connection_details': {
                    'host': row['Management IP'],  # Use the Management IP from the CSV
                    'username': row['Username'].strip(),  # Ensure any leading/trailing spaces are removed
                    'password': row['Password'].strip(),  # Ensure any leading/trailing spaces are removed
                    'method': primary_method  # Use the first method from the CSV (HTTPS or SSH)
                }
            }
            
            # Handle SD-WAN specific variables, if applicable
            if row['Device Type'] == 'SD-WAN Device':
                device['sd_wan_var'] = row.get('sd-wan var', 'N/A').strip()  # Use 'N/A' if no value
                device['sd_wan_var_value'] = row.get('sd-wan var value', 'N/A').strip()  # Use 'N/A' if no value

            inventory['networking_devices_for_vlan_changes'].append(device)

    # Write the inventory.yaml file
    with open(yaml_file, 'w') as yamlfile:
        yaml.dump(inventory, yamlfile, default_flow_style=False)

# Example usage
csv_file = 'device_inventory.csv'  # Replace with the path to your CSV file
yaml_file = 'inventory.yaml'  # The output YAML file
create_inventory_from_csv(csv_file, yaml_file)
