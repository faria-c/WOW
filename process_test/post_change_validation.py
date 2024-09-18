import os
import yaml
import logging

# Set up logging
logging.basicConfig(filename='post_change_validation.log', level=logging.INFO)

# Function to validate configurations
def validate_config(device):
    pre_change_file = f"{device['hostname']}_pre_change.txt"
    post_change_file = f"{device['hostname']}_post_change.txt"

    logging.info(f"Validating configuration for {device['hostname']}")

    try:
        # Ensure both pre and post change files exist
        if os.path.exists(pre_change_file) and os.path.exists(post_change_file):
            with open(pre_change_file, 'r') as pre_file, open(post_change_file, 'r') as post_file:
                pre_change_config = pre_file.read()
                post_change_config = post_file.read()

                # Compare the configurations
                if pre_change_config == post_change_config:
                    logging.info(f"No changes detected for {device['hostname']}.")
                else:
                    logging.info(f"Configuration changes detected for {device['hostname']}.")
                    # Check for specific VLAN changes (e.g., VLAN 400)
                    if "vlan 400" in post_change_config:
                        logging.info(f"VLAN 400 exists in the post-change configuration for {device['hostname']}.")
                    else:
                        logging.error(f"VLAN 400 was not found in the post-change configuration for {device['hostname']}.")
        else:
            logging.error(f"Pre or post change file not found for {device['hostname']}.")

    except Exception as e:
        logging.error(f"Error validating configuration for {device['hostname']}: {str(e)}")


# Load inventory from YAML file
with open('inventory.yaml', 'r') as file:
    inventory = yaml.safe_load(file)

# Validate configurations for all devices in the inventory
for device in inventory['devices']:
    validate_config(device)
