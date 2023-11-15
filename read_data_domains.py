import requests
import os
from requests.auth import HTTPBasicAuth
import yaml
from dotenv import load_dotenv

load_dotenv()

access_token = os.getenv('access_token')

def read_yaml_from_github(access_token):
    # GitHub API endpoint for raw content
    raw_url = f'https://raw.githubusercontent.com/hmrc/cip-data-domain-mapping/main/data-domain-to-audit-source-mapping.yaml'

    # Make a GET request with the personal access token for authentication
    response = requests.get(raw_url, auth=HTTPBasicAuth('token', access_token))

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the YAML content
        yaml_content = yaml.safe_load(response.text)
        return yaml_content
    else:
        print(f"Failed to fetch YAML file. Status code: {response.status_code}")
        return None

# Replace these values with your repository details and personal access token

# Read YAML content from the private GitHub repository
yaml_data = read_yaml_from_github(access_token)
audit_source = 'income-tax-subscription-eligibility;submit-vat-return-frontend;import-control-entry-declaration-outcome;fake-audit-source'

def find_data_domains(yaml_data, audit_source):

    if yaml_data:
        print({"Response":"Successfully obtained yaml data from repo"})

    audit_source_list = audit_source.split(';')
    data_domain_list = []

    for key, values in yaml_data.items():
        for audit_sources in audit_source_list:
            if audit_sources in values:

                data_domain_list.append(key)
                print(f'{key}: {audit_sources}')
            # else:
            #     data_domain_list.append(f'{audit_sources} not found')

    return set(data_domain_list)

if __name__=='__main__':
    yaml_data2 = read_yaml_from_github(access_token)
    data_doms = find_data_domains(yaml_data2, audit_source)
    print(data_doms)


