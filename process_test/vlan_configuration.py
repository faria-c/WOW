import paramiko
import yaml
import logging
import time

# Set up logging
logging.basicConfig(filename='vlan_configuration.log', level=logging.INFO)

def send_command(shell, command, sleep=2):
    """Send a command to the device and handle possible socket issues."""
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
            time.sleep(2)  # Give the shell time to initialize

            # Flush the shell buffer
            remote_conn.recv(65535).decode("utf-8")

            # Check if VLAN exists
            check_vlan_command = f"show vlan brief | include {vlan_id}"
            logging.info(f"Running VLAN check command on {device['hostname']}: {check_vlan_command}")
            vlan_check_output = send_command(remote_conn, check_vlan_command, 2)

            if vlan_check_output and str(vlan_id) in vlan_check_output:
                logging.info(f"VLAN {vlan_id} already exists on {device['hostname']}.")

                # Detailed VLAN Configuration and Trunk Port Check
                detailed_vlan_config_command = f"show run | section vlan {vlan_id}"
                detailed_vlan_config_output = send_command(remote_conn, detailed_vlan_config_command, 2)
                logging.info(f"Detailed VLAN {vlan_id} configuration on {device['hostname']}: {detailed_vlan_config_output}")

                # Check and add VLAN to trunk ports
                for trunk_port in ["GigabitEthernet1/0/1", "GigabitEthernet1/0/2"]:
                    trunk_check_command = f"show running-config interface {trunk_port}"
                    trunk_config = send_command(remote_conn, trunk_check_command, 2)
                    if trunk_config:
                        logging.info(f"Trunk port {trunk_port} config on {device['hostname']}: {trunk_config}")
                        if f"switchport trunk allowed vlan {vlan_id}" not in trunk_config:
                            logging.warning(f"Trunk port {trunk_port} does not allow VLAN {vlan_id} on {device['hostname']}.")
                            # Adding VLAN to trunk port
                            add_vlan_command = f"configure terminal\ninterface {trunk_port}\nswitchport trunk allowed vlan add {vlan_id}\nexit\nend"
                            send_command(remote_conn, add_vlan_command, 2)
                            logging.info(f"Added VLAN {vlan_id} to trunk port {trunk_port} on {device['hostname']}.")
                    else:
                        logging.error(f"Failed to retrieve config for {trunk_port} on {device['hostname']}.")
            else:
                logging.error(f"VLAN {vlan_id} not found on {device['hostname']} or failed to retrieve VLAN info.")
            
            ssh.close()

    except Exception as e:
        logging.error(f"Error configuring VLAN on {device['hostname']}: {str(e)}")

# Load inventory from YAML file
with open('inventory.yaml', 'r') as file:
    inventory = yaml.safe_load(file)

# Configure VLAN for networking devices only
for device in inventory.get('networking_devices_for_vlan_changes', []):
    configure_vlan(device)
