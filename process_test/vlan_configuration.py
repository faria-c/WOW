import paramiko
import yaml
import logging

# Set up logging
logging.basicConfig(filename='vlan_configuration.log', level=logging.INFO)

def configure_vlan(device, vlan_id=400):
    logging.info(f"Connecting to {device['hostname']} at {device['connection_details']['host']}")
    
    try:
        if device['connection_details']['method'] == 'SSH':
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(device['connection_details']['host'], 
                        username=device['connection_details']['username'], 
                        password=device['connection_details']['password'])

            # Check if VLAN exists
            check_vlan_command = f"show vlan brief | include {vlan_id}"
            stdin, stdout, stderr = ssh.exec_command(check_vlan_command)
            output = stdout.read().decode()

            if str(vlan_id) in output:
                logging.info(f"VLAN {vlan_id} already exists on {device['hostname']}.")
            else:
                logging.info(f"VLAN {vlan_id} does not exist on {device['hostname']}. Creating VLAN.")
                # Create VLAN and update trunk ports
                create_vlan_command = f"vlan {vlan_id}\nexit"
                ssh.exec_command(create_vlan_command)

                # Update trunk ports (this is a simplified example)
                for trunk_port in ["GigabitEthernet1/0/1", "GigabitEthernet1/0/2"]:  # Adjust based on your network
                    trunk_command = f"interface {trunk_port}\nswitchport trunk allowed vlan add {vlan_id}\nexit"
                    ssh.exec_command(trunk_command)

                logging.info(f"VLAN {vlan_id} configured on {device['hostname']}.")

            ssh.close()

    except Exception as e:
        logging.error(f"Error configuring VLAN on {device['hostname']}: {str(e)}")

# Load inventory from YAML file
with open('inventory.yaml', 'r') as file:
    inventory = yaml.safe_load(file)

# Configure VLAN for all devices
for device in inventory['devices']:
    configure_vlan(device)
