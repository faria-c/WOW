import yaml
import requests
import logging
from requests.exceptions import ConnectionError

# Set up logging
logging.basicConfig(filename='sdwan_health_check.log', level=logging.INFO)

# Function to read inventory from the YAML file
def read_inventory(file):
    with open(file, 'r') as f:
        return yaml.safe_load(f)

# Function to authenticate with vManage using REST API
def authenticate_vmanage(vmanage_host, username, password):
    base_url = f"https://{vmanage_host}:8443/"
    auth_url = base_url + "j_security_check"

    # Authentication data
    data = {
        'j_username': username,
        'j_password': password
    }
    
    # Creating a session to hold cookies
    session = requests.session()
    session.verify = False  # Disable SSL certificate verification

    try:
        # Performing the authentication
        response = session.post(auth_url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        if response.status_code == 200 and "html" not in response.text:
            logging.info(f"Authenticated successfully with vManage {vmanage_host}")
            return session
        else:
            logging.error(f"Authentication failed with vManage {vmanage_host}, Status Code: {response.status_code}")
            return None

    except ConnectionError as ce:
        logging.error(f"Failed to connect to vManage {vmanage_host}: {ce}")
        return None

# Function to check SD-WAN device status from vManage
def check_device_status_vmanage(session, vmanage_host):
    base_url = f"https://{vmanage_host}:8443/"
    
    # API to get device status
    url = base_url + "dataservice/device"
    
    try:
        response = session.get(url)
        if response.status_code == 200:
            devices = response.json()["data"]
            for device in devices:
                logging.info(f"Device: {device['host-name']}, Reachability: {device['reachability']}, "
                             f"BFD Sessions: {device['bfdSessionsUp']}, Status: {device['status']}")
        else:
            logging.error(f"Failed to retrieve device data from vManage {vmanage_host}, Status Code: {response.status_code}")
    
    except ConnectionError as ce:
        logging.error(f"Failed to connect to vManage {vmanage_host}: {ce}")

# Main function to process the devices from the inventory
def process_devices_from_inventory(inventory):
    for device in inventory['networking_devices_for_vlan_changes']:
        host = device['connection_details']['host']
        method = device['connection_details']['method']
        username = device['connection_details']['username']
        password = device['connection_details']['password']
        device_type = device['device_type']
        
        if device_type == "vManage":
            # Authenticate and check vManage health
            session = authenticate_vmanage(host, username, password)
            if session:
                check_device_status_vmanage(session, host)
        else:
            logging.info(f"Skipping {device_type} device {host}, only vManage will be checked using API.")

# Load inventory and run the process
inventory = read_inventory('inventory.yaml')
process_devices_from_inventory(inventory)
