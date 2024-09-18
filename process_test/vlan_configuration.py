import paramiko
import yaml
import logging
import time

# Set up logging
logging.basicConfig(filename='vlan_configuration.log', level=logging.INFO)

def send_command(shell, command, sleep=1):
    """Send a command to the device, handle --More-- prompts, and flush the buffer."""
    shell.send(command + '\n')
    time.sleep(sleep)
    output = ""
    
    while True:
        if shell.recv_ready():
            chunk = shell.recv(65535).decode("utf-8")
            output += chunk
            if "--More--" in chunk:
                shell.send(" ")  # Send space to continue
            else:
                break
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

            # Check if VLAN exists before entering config-transaction mode
            check_vlan_command = f"show vlan brief | include {vlan_id}"
            logging.info(f"Running VLAN check command on {device['hostname']}: {check_vlan_command}")
            vlan_check_output = send_command(remote_conn, check_vlan_command, 2)

            if str(vlan_id) in vlan_check_output:
                logging.info(f"VLAN {vlan_id} already exists on {device['hostname']}. Skipping configuration.")
            else:
                # If VLAN does not exist, enter configuration mode or config-transaction mode
                output = send_command(remote_conn, "show version", 1)
                if "Controller mode" in output:
                    logging.info(f"{device['hostname']} is in Controller mode, using config-transaction.")
                    send_command(remote_conn, "config-transaction", 1)
                else:
                    logging.info(f"{device['hostname']} is not in Controller mode, using configure terminal.")
                    send_command(remote_conn, "configure terminal", 1)

                # Create VLAN
                vlan_create_command = f"vlan {vlan_id}"
                logging.info(f"Creating VLAN {vlan_id} on {device['hostname']}")
                send_command(remote_conn, vlan_create_command, 1)
                send_command(remote_conn, "exit", 1)

                # Update trunk ports (adjust based on your network)
                for trunk_port in ["GigabitEthernet1/0/1", "GigabitEthernet1/0/2"]:  # Adjust based on your network
                    trunk_command = f"interface {trunk_port}\nswitchport trunk allowed vlan add {vlan_id}"
                    logging.info(f"Running trunk port update command on {device['hostname']}: {trunk_command}")
                    send_command(remote_conn, trunk_command, 1)
                    send_command(remote_conn, "exit", 1)

                logging.info(f"VLAN {vlan_id} and trunk configuration completed on {device['hostname']}.")

                # Exit configuration mode or commit transaction
                if "Controller mode" in output:
                    send_command(remote_conn, "commit", 1)
                else:
                    send_command(remote_conn, "end", 1)

            ssh.close()

    except Exception as e:
        logging.error(f"Error configuring VLAN on {device['hostname']}: {str(e)}")

# Load inventory from YAML file
with open('inventory.yaml', 'r') as file:
    inventory = yaml.safe_load(file)

# Configure VLAN for networking devices only
for device in inventory.get('networking_devices_for_vlan_changes', []):
    configure_vlan(device)
