import paramiko
import yaml
import logging
import time

# Set up logging
logging.basicConfig(filename='vlan_configuration.log', level=logging.INFO)

def send_command(shell, command, sleep=1):
    """Send a command to the device, handle --More-- prompts, and flush the buffer."""
    try:
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
    except Exception as e:
        logging.error(f"Failed to send command: {command}. Error: {str(e)}")
        return None

def configure_vlan(device, vlan_id=400):
    logging.info(f"Connecting to {device['hostname']} at {device['connection_details']['host']}")
    
    try:
        if device['connection_details']['method'] == 'SSH':
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            try:
                ssh.connect(device['connection_details']['host'], 
                            username=device['connection_details']['username'], 
                            password=device['connection_details']['password'],
                            look_for_keys=False, allow_agent=False)
            except paramiko.AuthenticationException:
                logging.error(f"Authentication failed for {device['hostname']}")
                return
            except paramiko.SSHException as e:
                logging.error(f"SSH connection error to {device['hostname']}: {str(e)}")
                return

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
                logging.info(f"VLAN {vlan_id} already exists on {device['hostname']}.")

                # **New Addition: Detailed VLAN Configuration and Trunk Port Check**
                detailed_vlan_config_command = f"show run | section vlan {vlan_id}"
                detailed_vlan_config_output = send_command(remote_conn, detailed_vlan_config_command, 2)
                logging.info(f"Detailed VLAN {vlan_id} configuration on {device['hostname']}: {detailed_vlan_config_output}")

                # Check if specific trunk ports allow the VLAN using running-config
                for trunk_port in ["GigabitEthernet1/0/1", "GigabitEthernet1/0/2"]:
                    trunk_check_command = f"show interface {trunk_port} switchport"
                    trunk_config = send_command(remote_conn, trunk_check_command, 2)
                    logging.info(f"Trunk port {trunk_port} config on {device['hostname']}: {trunk_config}")
                    
                    if f"switchport trunk allowed vlan {vlan_id}" in trunk_config:
                        logging.info(f"Trunk port {trunk_port} allows VLAN {vlan_id} on {device['hostname']}.")
                    else:
                        logging.warning(f"Trunk port {trunk_port} does not allow VLAN {vlan_id} on {device['hostname']}.")
                        # Adding VLAN to trunk port
                        logging.info(f"Adding VLAN {vlan_id} to trunk port {trunk_port} on {device['hostname']}.")
                        add_vlan_command = f"configure terminal\ninterface {trunk_port}\nswitchport trunk allowed vlan add {vlan_id}\nexit\nend"
                        send_command(remote_conn, add_vlan_command, 1)

            else:
                # If VLAN does not exist, enter configuration mode or config-transaction mode
                output = send_command(remote_conn, "enable", 1)
                output += send_command(remote_conn, "show version", 1)

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
                for trunk_port in ["GigabitEthernet1/0/1", "GigabitEthernet1/0/2"]:
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
