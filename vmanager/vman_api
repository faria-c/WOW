import yaml
import requests
import logging
import urllib3
from requests.exceptions import ConnectionError, Timeout

# Suppress the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
        
        # Log the response content for debugging purposes
        logging.debug(f"Authentication response content: {response.text}")

        # Successful authentication response should not contain "html"
        if response.status_code == 200 and "html" not in response.text:
            logging.info(f"Authenticated successfully with vManage {vmanage_host}")
            return session
        else:
            logging.error(f"Authentication failed with vManage {vmanage_host}, Status Code: {response.status_code}")
            logging.error(f"Response content: {response.text}")  # Log the actual response content for more insight
            return None

    except ConnectionError as ce:
        logging.error(f"Failed to connect to vManage {vmanage_host}: {ce}")
        return None
    except Timeout as te:
        logging.error(f"Request to vManage {vmanage_host} timed out: {te}")
        return None

# Function to get device health from vManage
def get_device_health(session, vmanage_host):
    base_url = f"https://{vmanage_host}:8443/"
    device_health_url = base_url + "dataservice/device"

    try:
        response = session.get(device_health_url)
        if response.status_code == 200:
            return response.json()["data"]
        else:
            logging.error(f"Failed to retrieve device health data from vManage {vmanage_host}, Status Code: {response.status_code}")
            return None

    except ConnectionError as ce:
        logging.error(f"Failed to connect to vManage {vmanage_host} while fetching device health: {ce}")
        return None
    except Timeout as te:
        logging.error(f"Request to vManage {vmanage_host} timed out while fetching device health: {te}")
        return None

# Function to log the health of each device
def log_device_health(devices):
    for device in devices:
        # Log relevant health details
        logging.info(f"Device: {device['host-name']}, Reachability: {device['reachability']}, "
                     f"BFD Sessions: {device.get('bfdSessionsUp', 'N/A')}, Status: {device['status']}, "
                     f"System IP: {device.get('system-ip', 'N/A')}")

        if device['status'] != "normal":
            logging.warning(f"Device {device['host-name']} has abnormal status: {device['status']}")
        if device['reachability'] != "reachable":
            logging.warning(f"Device {device['host-name']} is not reachable.")

# Main function to process the inventory and check device health
def process_devices_from_inventory(inventory):
    for device in inventory['networking_devices_for_vlan_changes']:
        host = device['connection_details']['host']  # Management IP
        username = device['connection_details']['username']
        password = device['connection_details']['password']
        device_type = device['device_type']
        
        # We only process vManage through the API
        if device_type == "vManage":
            logging.info(f"Processing vManage device {host}.")

            # Authenticate with vManage
            session = authenticate_vmanage(host, username, password)
            if session:
                # Fetch device health data from vManage
                devices = get_device_health(session, host)
                if devices:
                    log_device_health(devices)
        else:
            logging.info(f"Skipping {device_type} device {host}, as only vManage API is used for health checks.")

# Load inventory and run the process
inventory = read_inventory('inventory.yaml')
process_devices_from_inventory(inventory)
