import paramiko
import yaml
import logging
import os

# Set up logging
logging.basicConfig(filename='pre_change_capture.log', level=logging.INFO)

def capture_pre_change_output(device, output_dir):
    logging.info(f"Connecting to {device['hostname']} at {device['connection_details']['host']}")
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        if device['connection_details']['method'] == 'SSH':
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(device['connection_details']['host'], 
                        username=device['connection_details']['username'], 
                        password=device['connection_details']['password'])

            stdin, stdout, stderr = ssh.exec_command("show running-config")
            config_output = stdout.read().decode('utf-8')

            # Save the output to a file in the specified directory
            output_file = os.path.join(output_dir, f"{device['hostname']}_pre_change.txt")
            with open(output_file, 'w') as file:
                file.write(config_output)
                
            logging.info(f"Captured pre-change config for {device['hostname']} and saved to {output_file}")
            ssh.close()

    except Exception as e:
        logging.error(f"Error capturing config from {device['hostname']}: {str(e)}")

# Load inventory from YAML file
with open('inventory.yaml', 'r') as file:
    inventory = yaml.safe_load(file)

# Define output directory
output_dir = 'pre_change_output'

# Capture pre-change configuration for all devices
for device in inventory['devices']:
    capture_pre_change_output(device, output_dir)
