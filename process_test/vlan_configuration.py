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
                        password=device['connection_details']['password'],
                        look_for_keys=False, allow_agent=False)

            # Enable keepalive to prevent session drops
            ssh.get_transport().set_keepalive(30)

            # Enter configuration mode
            stdin, stdout, stderr = ssh.exec_command("configure terminal")
            config_output = stdout.read().decode()
            config_error_output = stderr.read().decode()

            if config_error_output:
                logging.error(f"Error entering configuration mode on {device['hostname']}: {config_error_output}")
                ssh.close()
                return

            # Check if VLAN exists
            check_vlan_command = f"show vlan brief | include {vlan_id}"
            logging.info(f"Running VLAN check command on {device['hostname']}: {check_vlan_command}")
            stdin, stdout, stderr = ssh.exec_command(check_vlan_command)
            output = stdout.read().decode()
            error_output = stderr.read().decode()

            if error_output:
                logging.error(f"Error during VLAN check on {device['hostname']}: {error_output}")
                ssh.close()
                return

            logging.info(f"VLAN check output for {device['hostname']}: {output}")

            if str(vlan_id) in output:
                logging.info(f"VLAN {vlan_id} already exists on {device['hostname']}.")
            else:
                logging.info(f"VLAN {vlan_id} does not exist on {device['hostname']}. Creating VLAN.")
                
                # Send the VLAN creation command
                stdin, stdout, stderr = ssh.exec_command(f"vlan {vlan_id}")
                vlan_output = stdout.read().decode()
                vlan_error_output = stderr.read().decode()

                if vlan_error_output:
                    logging.error(f"Error creating VLAN on {device['hostname']}: {vlan_error_output}")
                else:
                    logging.info(f"VLAN {vlan_id} created successfully on {device['hostname']}.")

                # Update trunk ports
                for trunk_port in ["GigabitEthernet1/0/1", "GigabitEthernet1/0/2"]:  # Adjust based on your network
                    trunk_command = f"interface {trunk_port}\nswitchport trunk allowed vlan add {vlan_id}\nexit"
                    logging.info(f"Running trunk port update command on {device['hostname']}: {trunk_command}")
                    stdin, stdout, stderr = ssh.exec_command(trunk_command)

                    trunk_output = stdout.read().decode()
                    trunk_error_output = stderr.read().decode()

                    if trunk_error_output:
                        logging.error(f"Error updating trunk port {trunk_port} on {device['hostname']}: {trunk_error_output}")
                    else:
                        logging.info(f"Trunk port {trunk_port} updated successfully on {device['hostname']}.")

            # Exit configuration mode
            stdin, stdout, stderr = ssh.exec_command("end")
            ssh.close()

    except Exception as e:
        logging.error(f"Error configuring VLAN on {device['hostname']}: {str(e)}")

# Load inventory from YAML file
with open('inventory.yaml', 'r') as file:
    inventory = yaml.safe_load(file)

# Configure VLAN for networking devices only
for device in inventory.get('networking_devices_for_vlan_changes', []):
    configure_vlan(device)
