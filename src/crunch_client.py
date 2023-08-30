################################################################################
#  Python Package to Support 42crunch System Deployment
#
#    Author: Sam Li <yang.li@owasp.org>
#
#       2022 - 2023
################################################################################

import requests, os, sys, re
import json, ruamel.yaml, base64
from .util import *
from os import mkdir
from os.path import dirname,realpath

class CrunchClient:
    def __init__(self, key, file, env):
        self.key = key
        self.crunch_headers = {
            'accept': 'application/json',
            'X-API-KEY': self.key
        }
        self.env = env
        self.env_pattern = re.compile( r'^\<%= ENV\[\'(.*)\'\] %\>(.*)$' )
        self.conf_dir = dirname(realpath(__file__)) + "/conf/"
        if not is_directory(self.conf_dir):
            mkdir(self.conf_dir)
        self.conf_file = file
        self.conf_dict = self.load_yaml(self.conf_file)
        self.address = self.conf_dict[env]['platform']['42c-addr']
        

    #  yaml module constructor for the parser
    def pathex_constructor(self, loader,node):
        value = loader.construct_scalar(node)
        envVar, remainingPath = self.env_pattern.match(value).groups()
        return os.environ[envVar] + remainingPath

    # loading configuration file
    def load_yaml(self, file):
        print("Loading instance configuration from file: ", file)
        ruamel.yaml.add_implicit_resolver ( "!pathex", self.env_pattern )
        ruamel.yaml.add_constructor('!pathex', self.pathex_constructor)
        with open(file, 'r') as f:
            conf_dict = ruamel.yaml.load(f, Loader=ruamel.yaml.Loader)
        return conf_dict

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        #os.unlink(file)
        pass

    # Retrieve 42crunch collection list from the platform
    def get_collection_list(self, uri):
        print("Make get request to endpoint ", uri)
        resp = requests.get(uri, headers=self.crunch_headers)
        collections = json.loads(resp.text)
        status_code = resp.status_code
        if status_code == 200:
            data = [x['desc'] for x in collections['list']]
            return data
        else:
            print("Error pulling collection endpoint: ", status_code)
            exit(1)

    # 42crunch create collection
    def create_collection(self, uri, name, verbose):
        print("Make post request to endpoint ", uri)
        payload = {
            "name": name,
            "isShared": True,
            "isSharedWrite": False
        }
        payload_str = json.dumps(payload).replace('\n','')
        if verbose:
            print('collection_uri: ', uri, '\ndata: ', payload, '\nheaders:', self.crunch_headers)
        resp = requests.post(uri, data=payload_str, headers=self.crunch_headers)
        if verbose:
            print(resp.text)
        return resp

    # Given a collection name, check if it's already exist
    def is_collection_exist(self, collections, name):
        for collection in collections:
            if collection['name'] == name:
                return True
        return False

    # Given collection name, return collection uuid
    def lookup_collection_id(self, collections, name):
        for c in collections:
            if c['name'] == name:
                return c['id']
        return None


    # Given swagger file, return swagger data in dict
    def get_swagger_dict(self, file, is_yaml):
        if is_yaml:
            with open(file, 'r', encoding='utf-8') as f:
                swagger_data = ruamel.yaml.load(f, Loader=ruamel.yaml.Loader)
        else:
            with open(file, 'rb') as f:
                swagger_data = json.load(f)
        return swagger_data

    # Given swagger file data dict, return 42c standard api name
    def get_api_name(self, swagger_data):
        api_name_raw = swagger_data['info']['title'] + '_' + swagger_data['info']['version']
        api_name = strip_non_alpha_num(api_name_raw)
        return api_name

    # Given a collection uuid, retrieve list of existing APIs
    def get_apis_by_cid(self, apis_uri, cid):
        print("Make get request to endpoint ", apis_uri)
        resp = requests.get(apis_uri, headers=self.crunch_headers)
        apis = json.loads(resp.text)
        status_code = resp.status_code
        if status_code == 200:
            return apis
        else:
            print("Error pulling collection endpoint for apis: ", status_code)
            exit(1)

    # Given api name and existing api list, determine if the api already exist
    def is_new_api(self, api_name, apis_list):
        print("Determine if api exist: ", api_name)
        for api in apis_list:
            if api['desc']['name'] == api_name:
                return False
        return True

    # Given api name and api list, return api id
    def get_api_id(self, api_name, apis_list):
        print("Retrieve API id for:", api_name)
        for api in apis_list:
            if api['desc']['name'] == api_name:
                print('Found: ', api['desc']['id'])
                return api['desc']['id']
        print('Not found')
        return ""

    # Given api uuid and api list, return api name
    def get_api_name_by_id(self, api_id, apis_list):
        print("Retrieve API name for:", api_id)
        for api in apis_list:
            if api['desc']['id'] == api_id:
                print('Found: ', api['desc']['name'])
                return api['desc']['name']
        print('Not found')
        return ""

    # API scan driver
    def scan_api(self, api_uuid, token, api_scan_url, verbose):
        platform_url = self.conf_dict[self.env]['platform']['42c-addr']
        specs_url = f"{platform_url}/api/v1/apis/{api_uuid}/specs"
        specs_payload = '{"filter": 256}'
        r = requests.post(specs_url, data=specs_payload, headers=self.crunch_headers)
        r.raise_for_status()
        security_section = r.json()["securitySchemes"]
        for key in security_section.keys():
            security_section[key]['apiKeyValue'] = token
        scan_config = {
            "host": api_scan_url,
            "security": security_section
        }
        json_config = json.dumps(scan_config).encode('utf-8')
        encoded_contents = base64.b64encode(json_config).decode('utf-8')
        payload = '{"config":"' + encoded_contents + '"}'
        if verbose:
            print('Base64 encoding the scan config: \npayload: ', payload)
        url = f"{platform_url}/api/v1/apis/{api_uuid}/scan"
        response = requests.post(url, data=payload, headers=self.crunch_headers)
        if response.status_code == 200:
            scan_id = response.json()['id']
            success = response.json()['success']
            if success:
                print(f"Successfully submitted scan for API: {api_uuid}")
                return scan_id
            else:
                print(
                    f"Platform success failure after scan submission response - code {response.status_code} and success code {success}")
                sys.exit(1)
        else:
            print(f"Scan init failed with status code {response.status_code}")
            sys.exit(1)

    # Given API name  / swagger file path / YAML format and collection ID, publishing it into 42Crunch platform
    def create_api(self, name, uri, file, cid, is_yaml, verbose):
        print("Make post request to endpoint ", uri)
        # preparing for swagger file data
        swagger_data = get_swagger_dict(file, is_yaml)
        api_name = self.get_api_name(swagger_data)
        multipart_form_data = {
            'specfile': (file, json.dumps(swagger_data, indent=2, default=str), 'application/json'),
            'name': ('', api_name),
            'cid': ('', cid)
        }
        if verbose:
            print('api_name: ', api_name, '\ncid: ', cid, '\nheaders:', self.crunch_headers, '\nswagger_data:', swagger_data)
        resp = requests.post(uri, files=multipart_form_data, headers=self.crunch_headers)
        if verbose:
            print(resp.text)
        return resp.status_code

    # Given API update url,  swagger file path / YAML format, update it in 42Crunch platform
    def update_api(self, uri, file, is_yaml, verbose):
        print("Make put request to endpoint ", uri)
        # preparing for swagger file data
        swagger_data = get_swagger_dict(file, is_yaml)
        json_contents_as_bytes = json.dumps(swagger_data, indent=2, default=str).encode('utf-8')
        b64_contents = base64.b64encode(json_contents_as_bytes).decode('utf-8')
        payload = '{"specfile":"' + b64_contents + '"}'
        resp = requests.put(uri, data=payload, headers=self.crunch_headers)
        if verbose:
            print(resp.text)
        return resp.status_code
