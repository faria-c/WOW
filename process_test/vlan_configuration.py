import paramiko
import yaml
import logging
import time

# Set up logging
logging.basicConfig(filename='vlan_configuration.log', level=logging.INFO)

def send_command(shell, command, sleep=1):
    """Send a command to the device and flush the buffer."""
    shell.send(command + '\n')
    time.sleep(sleep)
    output = shell.recv(65535).decode("utf-8")
    return output

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

            # Flush the shell buffer
            remote_conn.recv(65535).decode("utf-8")

            # Determine whether the device is in Controller mode
            output = send_command(remote_conn, "enable", 1)
            output += send_command(remote_conn, "show version", 1)

            if "Controller mode" in output:
                logging.info(f"{device['hostname']} is in Controller mode, using config-transaction.")
                output += send_command(remote_conn, "config-transaction", 1)
            else:
                logging.info(f"{device['hostname']} is not in Controller mode, using configure terminal.")
                output += send_command(remote_conn, "configure terminal", 1)

            # Check if VLAN exists
            check_vlan_command = f"show vlan brief | include {vlan_id}"
            logging.info(f"Running VLAN check command on {device['hostname']}: {check_vlan_command}")
            output += send_command(remote_conn, check_vlan_command, 2)
            logging.info(f"VLAN check output for {device['hostname']}: {output}")

            if str(vlan_id) in output:
                logging.info(f"VLAN {vlan_id} already exists on {device['hostname']}.")
            else:
                logging.info(f"VLAN {vlan_id} does not exist on {device['hostname']}. Creating VLAN.")
                
                # Create VLAN
                output += send_command(remote_conn, f"vlan {vlan_id}", 1)
                output += send_command(remote_conn, "exit", 1)

                # Update trunk ports (this is a simplified example)
                for trunk_port in ["GigabitEthernet1/0/1", "GigabitEthernet1/0/2"]:  # Adjust based on your network
                    trunk_command = f"interface {trunk_port}\nswitchport trunk allowed vlan add {vlan_id}"
                    logging.info(f"Running trunk port update command on {device['hostname']}: {trunk_command}")
                    output += send_command(remote_conn, trunk_command, 1)
                    output += send_command(remote_conn, "exit", 1)

                logging.info(f"VLAN {vlan_id} and trunk configuration completed on {device['hostname']}.")

            # Exit configuration mode or commit transaction
            if "Controller mode" in output:
                output += send_command(remote_conn, "commit", 1)
            else:
                output += send_command(remote_conn, "end", 1)
            ssh.close()

    except Exception as e:
        logging.error(f"Error configuring VLAN on {device['hostname']}: {str(e)}")

# Load inventory from YAML file
with open('inventory.yaml', 'r') as file:
    inventory = yaml.safe_load(file)

# Configure VLAN for networking devices only
for device in inventory.get('networking_devices_for_vlan_changes', []):
    configure_vlan(device)
