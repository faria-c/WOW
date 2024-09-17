import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Function to authenticate with vManage API and retrieve the session token
def authenticate_vmanage(vmanage_host, username, password):
    url = f"https://{vmanage_host}/j_security_check"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'j_username': username, 'j_password': password}

    session = requests.session()
    response = session.post(url, headers=headers, data=payload, verify=False)

    if response.status_code == 200 and 'Set-Cookie' in response.headers:
        print("Authenticated with vManage.")
        return session
    else:
        print("Failed to authenticate with vManage.")
        response.raise_for_status()

# Function to get the list of device templates and return a valid masterTemplateId
def get_master_template_id(vmanage_host, session):
    api_url = f"https://{vmanage_host}/dataservice/template/device"
    headers = {'Content-Type': 'application/json'}
    
    response = session.get(api_url, headers=headers, verify=False)
    
    if response.status_code == 200:
        templates = response.json()
        if 'data' in templates:
            # Loop through available templates and print them
            for template in templates['data']:
                print(f"Template Name: {template['templateName']}, Template ID: {template['templateId']}")
            
            # For simplicity, return the first template ID (you can update this logic)
            return templates['data'][0]['templateId']
        else:
            print("No templates found.")
            return None
    else:
        print(f"Failed to retrieve templates. Status code: {response.status_code}")
        response.raise_for_status()

# Function to retrieve SD-WAN site variable files via vManage API
def retrieve_sdwan_site_variables(vmanage_host, session, master_template_id):
    api_url = f"https://{vmanage_host}/dataservice/template/device/config/attached/{master_template_id}"
    headers = {'Content-Type': 'application/json'}
    
    response = session.get(api_url, headers=headers, verify=False)

    if response.status_code == 200:
        data = response.json()
        # Iterate through all devices/sites to retrieve variable files
        for device in data.get('data', []):
            device_id = device.get('uuid')
            template_name = device.get('template')
            print(f"Retrieving variable file for Device ID: {device_id}, Template: {template_name}")
            
            if device_id:
                # Get the variable file for the specific device
                var_file_api_url = f"https://{vmanage_host}/dataservice/template/device/config/input/{device_id}"
                var_response = session.get(var_file_api_url, headers=headers, verify=False)
                
                if var_response.status_code == 200:
                    var_data = var_response.json()
                    # Print or save the variable file data
                    with open(f"{device_id}_variables.json", 'w') as outfile:
                        json.dump(var_data, outfile, indent=4)
                    print(f"Variable file for {device_id} saved successfully.")
                else:
                    print(f"Failed to retrieve variable file for Device ID: {device_id}. Status code: {var_response.status_code}")
            else:
                print(f"Device ID missing for a device in the template {template_name}")
    else:
        print(f"Failed to retrieve device list. Status code: {response.status_code}")
        print(response.text)

# Example usage
vmanage_host = "192.168.0.50"  # Replace with vManage host IP or hostname
username = "labuser"  # Replace with vManage username
password = "Labpass01!"  # Replace with vManage password

# Authenticate and retrieve site variables
try:
    session = authenticate_vmanage(vmanage_host, username, password)
    if session:
        # Get a valid masterTemplateId
        master_template_id = get_master_template_id(vmanage_host, session)
        if master_template_id:
            # Use the retrieved masterTemplateId to get site variables
            retrieve_sdwan_site_variables(vmanage_host, session, master_template_id)
        else:
            print("No valid template ID found.")
except requests.exceptions.RequestException as e:
    print(f"Error occurred: {e}")
