import paramiko
import yaml
import logging
import time

# Set up logging
logging.basicConfig(filename='vlan_configuration.log', level=logging.INFO)

def send_command(shell, command, sleep=1):
    """Send a command to the device and wait for the response."""
    shell.send(command + '\n')
    time.sleep(sleep)
    output = ""
    
    while shell.recv_ready():
        chunk = shell.recv(65535).decode("utf-8")
        output += chunk
        if "--More--" in chunk:
            shell.send(" ")  # Press space to continue
    return output

def configure_vlan(device, vlan_id=400):
    logging.info(f"Connecting to {device['hostname']} at {device['connection_details']['host']}")
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the device
        ssh.connect(device['connection_details']['host'], 
                    username=device['connection_details']['username'], 
                    password=device['connection_details']['password'],
                    look_for_keys=False, allow_agent=False)

        # Open interactive shell
        remote_conn = ssh.invoke_shell()
        time.sleep(1)  # Give the shell time to initialize

        # Flush the shell buffer
        remote_conn.recv(65535).decode("utf-8")

        # Check if VLAN 400 exists
        check_vlan_command = "show vlan brief"
        logging.info(f"Running VLAN check command on {device['hostname']}: {check_vlan_command}")
        vlan_check_output = send_command(remote_conn, check_vlan_command, 2)

        if f"{vlan_id}" in vlan_check_output:
            logging.info(f"VLAN {vlan_id} already exists on {device['hostname']}.")
        else:
            # Enter configuration mode and create VLAN 400
            send_command(remote_conn, "configure terminal", 1)
            send_command(remote_conn, f"vlan {vlan_id}", 1)
            send_command(remote_conn, "exit", 1)

            logging.info(f"VLAN {vlan_id} created on {device['hostname']}.")
        
        # Configure trunk ports to allow VLAN 400
        trunk_ports = ["GigabitEthernet1", "GigabitEthernet2"]  # Modify as per your network
        for port in trunk_ports:
            logging.info(f"Configuring trunk port {port} to allow VLAN {vlan_id} on {device['hostname']}.")
            send_command(remote_conn, "configure terminal", 1)
            send_command(remote_conn, f"interface {port}", 1)
            send_command(remote_conn, f"switchport trunk allowed vlan add {vlan_id}", 1)
            send_command(remote_conn, "exit", 1)
        
        # Verify VLAN and trunk port configuration
        for port in trunk_ports:
            interface_output = send_command(remote_conn, f"show running-config interface {port}", 2)
            logging.info(f"Configuration of {port} on {device['hostname']}: {interface_output}")

        # Verify that VLAN 400 was created
        vlan_output = send_command(remote_conn, "show vlan brief", 2)
        logging.info(f"VLAN configuration on {device['hostname']}: {vlan_output}")

        # Close the SSH connection
        ssh.close()

    except Exception as e:
        logging.error(f"Error configuring VLAN on {device['hostname']}: {str(e)}")
        # Optionally, try to reconnect and continue configuration

# Load inventory from YAML file
with open('inventory.yaml', 'r') as file:
    inventory = yaml.safe_load(file)

# Configure VLAN for networking devices only
for device in inventory.get('networking_devices_for_vlan_changes', []):
    configure_vlan(device)
