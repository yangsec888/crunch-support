################################################################################
#  Python Package to Support 42crunch System Deployment
#
#    Author: Sam Li <yang.li@owasp.org>
#
#       2022 - 2023
################################################################################
import requests, json
from lxml import html
from seleniumwire import webdriver
from seleniumwire.utils import decode
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

token_service_headers  = {
    'Content-Type': 'application/json'
}

# Given API configuration, retrieve a valid token for the API scan
def get_token(api_conf, conf_dict, env, verbose):
    print(f"Request a valid token for api scan: {api_conf['api-scan-url']}")
    token=None
    if api_conf['authen-type'] == 'm2m':
        uri = conf_dict[env]['cloud-security']['m2m-token-uri'] + conf_dict[env]['cloud-security']['server-id'] + '/token'
        payload = {
            "clientId": conf_dict[env]['cloud-security']['client-id'],
            "clientSecret": conf_dict[env]['cloud-security']['client-secret']
        }
        token = get_m2m_token(uri, payload, verbose)
    elif api_conf['authen-type'] == 'null':
        token = None
    elif api_conf['authen-type'] == 'pdm':
        token = get_pdm_token(conf_dict, env)
    elif api_conf['authen-type'] == 'discover_pwd':
        token = get_discover_pwd_token(conf_dict, env, verbose)
    return token

# Given uri and payload, retrieve m2m token
def get_m2m_token(uri, payload, verbose):
    resp = requests.post(uri, headers=token_service_headers, json=payload)
    if verbose:
        print(f'Request uri: {uri}, header: {token_service_headers}, payload: {payload}')
        print(resp.text)
    if resp.status_code == 200:
        return resp.json()['accessToken']
    else:
        print(f'Invalid request to uri: {uri} Error code: {resp.status_code}')
        return None

# Walk though cloud OAuth 2.0 Client Credential grant flow implementation, in order to retrieve a scan token 
def get_pdm_token(conf_dict, env):
    session_token = get_okta_session_token(conf_dict, env)
    print('Retrieve session token: ', session_token)
    auth_code = get_auth_code(session_token, conf_dict, env)
    print('Retrieve auth code: ', auth_code)
    token = code_2_token(conf_dict, env, auth_code)
    print('Retrieve scan token: ', token)
    return token

# Get a session token as the first step, before calling the auth-bridge service
def get_okta_session_token(conf_dict, env):
    payload = {
        "username": conf_dict[env]['cloud-security']['pdm-srv-usr'],
        "password": conf_dict[env]['cloud-security']['pdm-srv-pass'],
        "options": {
            "multiOptionalFactorEnroll": True,
            "warnBeforePasswordExpired": True
        }
    }
    resp = requests.post(conf_dict[env]['cloud-security']['okta-client-credential-grant-start-uri'], headers=token_service_headers, json=payload)
    if resp.status_code == 200:
        return resp.json()['sessionToken']
    else:
        okta_client_credential_grant_start_uri = conf_dict[env]['cloud-security']['okta-client-credential-grant-start-uri']
        print(f'Invalid request to uri: {okta_client_credential_grant_start_uri} Error code: {resp.status_code}')
        return None

# Get an authen code as the 2nd step, before calling the auth-bridge service
def get_auth_code(session_token, conf_dict, env):
    uri =  conf_dict[env]['cloud-security']['okta-client-oauth-auth-uri'] + session_token + '&state=foox'
    okta_default_cookies = {
        'DT': conf_dict[env]['cloud-security']['okta-default-cookies-dt'],
        'JSESSIONID': conf_dict[env]['cloud-security']['okta-default-cookies-jid'],
        'sid': conf_dict[env]['cloud-security']['okta-default-cookies-sid'],
        't': 'default'
    }
    resp = requests.get(
        uri, 
        cookies=okta_default_cookies, 
    )
    #print(f'uri:  {uri}, \ncookie: {okta_default_cookies}')
    if resp.status_code == 200:
        page = resp.text.encode('utf-8')
        #print('page: ', page)
        tree = html.fromstring(page)
        code = tree.xpath('//input[@name="code"]/@value')
        return code[0]
    else:
        print(f'Invalid request to uri: {uri} Error code: {resp.status_code}')
        return None

# Call auth-bridge service to exchange code for token
def code_2_token(conf_dict, env, code):
    uri = conf_dict[env]['cloud-security']['pdm-token-uri'] 
    print(conf_dict[env]['cloud-security'])
    json_data = {
        'clientId': conf_dict[env]['cloud-security']['client-id-2'],
        'clientSecret': conf_dict[env]['cloud-security']['client-secret-2'],
        'code': code,
        'redirectUri': conf_dict[env]['cloud-security']['client-redirection-url-2'],
    }
    #print(f'uri: {uri}, \nheaders: {token_service_headers}, \njson: {json_data}')
    resp = requests.post(uri, headers=token_service_headers, json=json_data,)
    if resp.status_code == 200:
        return resp.json()['accessToken']
    else:
        print(f'Invalid request to uri: {uri} Error code: {resp.status_code}')
        return None

# Web scrapping to retrieve DMS service token, refer to example: https://www.scrapingbee.com/blog/selenium-python/ 
def get_discover_pwd_token(conf_dict, env, verbose):
    # web scraping using selenium
    token = None 
    uri = conf_dict[env]['dms-security']['pwd-start-uri']
    caps = DesiredCapabilities.CHROME.copy()
    caps["goog:loggingPrefs"] = {"performance": "ALL"}  # enable performance logs
    driver_path = conf_dict[env]['dms-security']['chrome-driver']
    chrome_options = Options()
    if not verbose:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument('--window-size=1280,1280')
        chrome_options.add_argument('--enable-javascript')
    mobile_emulation = {
        "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },
        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    driver = webdriver.Chrome(options=chrome_options, executable_path=driver_path, desired_capabilities=caps)
    driver.set_page_load_timeout(120)
    # set implicit wait to 20 seconds
    driver.implicitly_wait(20)
    if verbose:
        print("User agent: ")
        print(driver.execute_script("return navigator.userAgent;"))
    try:
        driver.get(uri)
        driver.find_element(By.ID, 'username').send_keys(conf_dict[env]['dms-security']['pwd-user'])
        driver.find_element(By.ID, 'Password').send_keys(conf_dict[env]['dms-security']['pwd-pass'])
        driver.find_element(By.CLASS_NAME, 'round-button').click()
        # set explicit wait to 25 seconds
        wait = WebDriverWait(driver, 25, poll_frequency=0.1)
        #wait.until(EC.title_is('Omnipod Discover'))
        wait.until(EC.url_contains('week'))
    except TimeoutException as ex:
        print("Exception detect:", ex.msg)
    # Access requests via the `requests` attribute
    for request in driver.requests:
        if request.response:
            body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
            if verbose: 
                print(request.url.lower())
            if 'oauth2' in request.url.lower() and 'token' in request.url.lower() and 'authorize' not in request.url.lower():
                data = json.loads(body)
                if verbose:
                    print('Oauth2 token response payload:', data)
                token = data['access_token']
                print("Access token found: ", token)
                return token 
    if verbose: 
        print(f'Current landing page: {driver.current_url}')
    print("Error scraping out discover app token")
    exit(1)
