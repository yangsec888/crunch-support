================================================================================
- [What is it?](#what-is-it)
  - [42Crunch](#42Crunch)
  - [42Crunch API Access](#42crunch-api-access)
- [Inside Toolbox](#inside-toolbox)
  - [api-audit](#api-audit)
  - [api-scan](#api-scan)
  - [api-protect](#api-protect)
- [Unit Test](#unit-test)
- [To Do](#to-do)
---

## What is it?
This is an inhouse build  python module for 42crunch platform support. [Download it](/dist/crunch_support-1.0-py3-none-any.whl) directly, before installing it into your local environment:
```bash
$ pip install crunch_support-1.0-py3-none-any.whl 
```
Once installed, the bundled utility scripts would also be placed into your local bin path. For example:
```bash
$ which api-audit
/usr/local/bin/api-audit
```
### 42Crunch
42Crunch is a specialist tool for cloud API security automation. The production system is software as a service (SaaS) platform hosted at the URI: <https://platform.us.42crunch.cloud/login> In order to access it, you'll need to contact the Security team for the access provision.

### 42Crunch API Access
42Crunch provides API access to its core platform functions. Refer to the 42Crunch postman collections for example: <https://www.postman.com/get-42crunch/workspace/42crunch-api/folder/13761657-a7ad81b7-11bc-4b6f-a379-5f53a900af92?ctx=documentation>


## Inside Toolbox
The following custom tools are available within this toolbox:

### api-audit
Automation script / workflow for Cloud API audit. For example, the script would read the configuration from the 'api-audit-cloud.yaml' file, then submit/update the OpenAPI swagger files into 42Crunch platform for audit accordingly:
```bash
$ api-audit -k $c_key_dev -b ~/apps/xxx/ -y src/conf/api-scan-xxx.yaml -e development 
...
Initiate a 42crunch client instance
Loading instance configuration from file:  src/conf/api-scan-xxx.yaml
Retrieve 42c collection list ...
Make get request to endpoint  https://platform.42crunch.com/api/v1/collections
Make post request to endpoint  https://platform.42crunch.com/api/v1/collections
Successfully create new collection in 42Crunch platform: xxx-xxx_insights_service
Update 42c colllection list accordingly
{"desc":{"id":"64e7de1a-4522-438e-9287-b53a9cea7463","name":"xxx-xxx_insights_service","technicalName":"64e7de1a-4522-438e-9287-b53a9cea7463","source":"default","isShared":true,"isSharedWrite":false},"summary":{"org":{"name":"xxx"},"read":true,"write":true,"writeApis":true,"apis":0},"protection":null,"owner":null,"userCounter":0,"teamCounter":0}
Make get request to endpoint  https://platform.42crunch.com/api/v1/collections/64e7de1a-4522-438e-9287-b53a9cea7463/apis
Perform git operations on repo:  xxx_insights_service
Start publishing swagger file:  xxx_open_apis , to collection:  xxx-xxx_insights_service
Determine if api exist:  xxxAPIforPWD_100
Make post request to endpoint  https://platform.42crunch.com/api/v1/apis
Swagger file upload for audit successfully
```

### api-scan
Automation script / workflow for Cloud API Conformance Scan. For example, the script would read the configuration from the 'api-scan-cloud.yaml' file, then itererate through the APIs to perform API conformation scans:
```bash
$ api-scan -k $c_key_dev -b ~/apps/xxx/ -y src/conf/api-scan-xxx.yaml -e development
...
Initiate a 42crunch client instance
Loading instance configuration from file:  src/conf/api-scan-xxx.yaml
Retrieve 42c collection list ...
Make get request to endpoint  https://platform.42crunch.com/api/v1/collections
Make get request to endpoint  https://platform.42crunch.com/api/v1/collections/64e7de1a-4522-438e-9287-b53a9cea7463/apis
Start scan api:  xxx_open_apis , in collection:  xxx-xxx_insights_service
Retrieve API id for: xxxAPIforPWD_100
Found:  de69a834-7dd8-4bb4-bd86-bde1be5d9d67
Prepare for API Scan Target:  https://qa.xxx.test.com
Request a valid token for api scan: https://qa.xxx.test.com
Access token found:  xxxxx
Use scan token:  xxxxx
Successfully submitted scan for API: de69a834-7dd8-4bb4-bd86-bde1be5d9d67
```

### api-protect
Automation script / workflow for Cloud API Protection. (TBD)


## Unit Test ##
[Unit test](/tests) are written to ensure the quality of the code. It provides the assurance and sustainability of the project. Use the following command to run the tests:

```bash
$ cd crunch-support/
$ python -m unittest xxx tests/
```


## To Do
TBD
