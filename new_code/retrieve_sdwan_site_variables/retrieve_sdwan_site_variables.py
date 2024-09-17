import requests
import json

# Function to authenticate with vManage API and retrieve the session token
def authenticate_vmanage(vmanage_host, username, password):
    url = f"https://{vmanage_host}/j_security_check"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'j_username': username, 'j_password': password}

    session = requests.session()
    response = session.post(url, headers=headers, data=payload, verify=False)

    if response.status_code == 200:
        print("Authenticated with vManage.")
        return session
    else:
        print("Failed to authenticate with vManage.")
        response.raise_for_status()

# Function to retrieve SD-WAN site variable files via vManage API
def retrieve_sdwan_site_variables(vmanage_host, session):
    api_url = f"https://{vmanage_host}/dataservice/template/device/config/attached"
    headers = {'Content-Type': 'application/json'}
    
    response = session.get(api_url, headers=headers, verify=False)

    if response.status_code == 200:
        data = response.json()
        # Iterate through all devices/sites to retrieve variable files
        for device in data['data']:
            device_id = device['uuid']
            template_name = device['template']
            print(f"Retrieving variable file for Device ID: {device_id}, Template: {template_name}")
            
            # Get the variable file for the specific device
            var_file_api_url = f"https://{vmanage_host}/dataservice/template/device/config/input/{device_id}"
            var_response = session.get(var_file_api_url, headers=headers, verify=False)
            
            if var_response.status_code == 200:
                var_data = var_response.json()
                # Print or save the variable file data
                with open(f"{device_id}_variables.json", 'w') as outfile:
                    json.dump(var_data, outfile, indent=4)
                print(f"Variable file for {device_id} saved.")
            else:
                print(f"Failed to retrieve variable file for Device ID: {device_id}")
    else:
        print("Failed to retrieve device list.")
        response.raise_for_status()

# Example usage
vmanage_host = "192.168.0.50"  # Replace with vManage host IP or hostname
username = "labuser"  # Replace with vManage username
password = "Labpass01!"  # Replace with vManage password

# Authenticate and retrieve site variables
session = authenticate_vmanage(vmanage_host, username, password)
retrieve_sdwan_site_variables(vmanage_host, session)
