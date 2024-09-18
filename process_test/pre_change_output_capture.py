import paramiko
import yaml
import logging

# Set up logging
logging.basicConfig(filename='pre_change_capture.log', level=logging.INFO)

def capture_pre_change_output(device):
    logging.info(f"Connecting to {device['hostname']} at {device['connection_details']['host']}")
    try:
        # Only SSH method shown here; HTTP/HTTPS would require different handling
        if device['connection_details']['method'] == 'SSH':
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(device['connection_details']['host'], 
                        username=device['connection_details']['username'], 
                        password=device['connection_details']['password'])
            
            stdin, stdout, stderr = ssh.exec_command("show running-config")
            config_output = stdout.read().decode('utf-8')
            
            # Save the output to a file for each device
            with open(f"{device['hostname']}_pre_change.txt", 'w') as file:
                file.write(config_output)
                
            logging.info(f"Captured pre-change config for {device['hostname']}")
            ssh.close()

    except Exception as e:
        logging.error(f"Error capturing config from {device['hostname']}: {str(e)}")

# Load inventory from YAML file
with open('inventory.yaml', 'r') as file:
    inventory = yaml.safe_load(file)

# Capture pre-change configuration for all devices
for device in inventory['devices']:
    capture_pre_change_output(device)
