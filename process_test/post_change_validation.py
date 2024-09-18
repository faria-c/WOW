import os
import logging

# Set up logging
logging.basicConfig(filename='post_change_validation.log', level=logging.INFO)

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
                    # You can further analyze the differences by checking for specific VLAN entries.
                    if "vlan 400" in post_change_config:
                        logging.info(f"VLAN 400 exists in the post-change configuration for {device['hostname']}.")
                    else:
                        logging.error(f"VLAN 400 was not found in the post-change configuration for {device['hostname']}.")

        else:
            logging.error(f"Pre or post change file not found for {device['hostname']}.")

    except Exception as e:
        logging.error(f"Error validating configuration for {device['hostname']}: {str(e)}")


# Example inventory to validate configurations (load from actual inventory.yaml)
inventory = [
    {"hostname": "BR1-cEdge-1"},
    {"hostname": "BR1-cEdge-2"},
    {"hostname": "BR2-cEdge-1"},
    {"hostname": "BR3-vEdge-1"},
    {"hostname": "BR4-Spoke1"}
]

# Validate configurations for all devices
for device in inventory:
    validate_config(device)
