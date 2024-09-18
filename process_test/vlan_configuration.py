import paramiko
import yaml
import logging
import time

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

            # Open interactive shell
            remote_conn = ssh.invoke_shell()
            time.sleep(1)  # Give the shell time to initialize

            # Enter enable mode if required
            remote_conn.send("enable\n")
            time.sleep(1)
            remote_conn.send("configure terminal\n")
            time.sleep(1)

            # Check if VLAN exists
            check_vlan_command = f"show vlan brief | include {vlan_id}\n"
            logging.info(f"Running VLAN check command on {device['hostname']}: {check_vlan_command}")
            remote_conn.send(check_vlan_command)
            time.sleep(2)  # Wait for the command to execute
            
            output = remote_conn.recv(65535).decode("utf-8")
            logging.info(f"VLAN check output for {device['hostname']}: {output}")
            
            if str(vlan_id) in output:
                logging.info(f"VLAN {vlan_id} already exists on {device['hostname']}.")
            else:
                logging.info(f"VLAN {vlan_id} does not exist on {device['hostname']}. Creating VLAN.")
                
                # Create VLAN
                remote_conn.send(f"vlan {vlan_id}\n")
                time.sleep(1)
                remote_conn.send("exit\n")
                time.sleep(1)

                # Update trunk ports (this is a simplified example)
                for trunk_port in ["GigabitEthernet1/0/1", "GigabitEthernet1/0/2"]:  # Adjust based on your network
                    trunk_command = f"interface {trunk_port}\nswitchport trunk allowed vlan add {vlan_id}\nexit\n"
                    logging.info(f"Running trunk port update command on {device['hostname']}: {trunk_command}")
                    remote_conn.send(trunk_command)
                    time.sleep(1)

                logging.info(f"VLAN {vlan_id} and trunk configuration completed on {device['hostname']}.")

            # Exit configuration mode
            remote_conn.send("end\n")
            time.sleep(1)
            ssh.close()

    except Exception as e:
        logging.error(f"Error configuring VLAN on {device['hostname']}: {str(e)}")

# Load inventory from YAML file
with open('inventory.yaml', 'r') as file:
    inventory = yaml.safe_load(file)

# Configure VLAN for networking devices only
for device in inventory.get('networking_devices_for_vlan_changes', []):
    configure_vlan(device)
