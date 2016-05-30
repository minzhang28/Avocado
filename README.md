# Avocado
This is a project to generate Vault token againest Vault APP-ID backend based on AWS EC2 Identity Document.

## Problem to solve
[Vault](https://www.vaultproject.io/) is a powerful service to manage and control secrets. In order to use Vault to generate new secrets or reading existing secrets, user has to have a token, which can be a risk of security. Avocado is to solve this chicken-and-egg problem.

## Use Cases
- Auto generate Vault token with specified Vault policy without knowing any existing Vault token
- Protect token request replays. Token only generated once from the same EC2, repeatable requests are ignored
- Easier `app-id` and `user-id` management than using Vault command line. Avocado saves project metadata (Vault policy, app-id, instance list, etc) in a consul K/V pair.
> Avocado is supposed to be running on a secure environment where only limited people has access

## How it works
![alt text](https://raw.githubusercontent.com/minzhang28/Avocado/master/Avocado.png)

1. Token requester send `POST` request to Avocado with it's [EC2 identity document](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-identity-documents.html) and the PKCS7 Signature
2. Avocado verifies the EC2 PKCS7 signature to make sure the token requester is from trusted source
3. Avocado checks if this EC2 is already in the list of instances on Consul K/V pairs, if true, ignores the request, otherwise, adds the metadata of token requester to the instance list
4. If both step #2 and #3 passed, Avocado calls Vault http `APP ID` auth backend API to create new `user-id` and map to existing `app-id`, then generate token based on pre-defined policy and return to token requester.
5. Since there's no lease period for the `APP ID` token, thus there's no need to renew

## Consul EC2 metadata
In order to proceed the instance check between Avocado and Consul, Consul must have following setups done:
- Naming convention:  `project_name + "/" + project_env`. This is pretty standard `KEY` pattern for Consul. For example, if the K/V pair belongs to `PRODUCTION` environment of project `DEMO`, then the keys should be `DEMO/PRODUCTION`. Avocado is following this pattern to automatically generate request URL.

- Metadata: To proceed the instance check, the JSON below needs to be saved as `Value` paired with the `Key` mentioned above:
```
{
  "project": "demo",
  "policy": "demo_production", # The policy name in Vault which all new Vault token use
  "app_id": "demo_production", # Optional, if not available, Avocado uses "project_environment" as app_id and create mapping on Vault.
  "instances":                 # Optional, Avocado checks if EC2 Mac address is registered before to avoid duplicate
    [
        {
          "devpayProductCodes": null,
          "availabilityZone": "us-west-00",
          "instanceId": "i-abcdefg",
          "region": "us-west-00",
          "privateIp": "172.0.0.0",
          "version": "2010-08-31",
          "architecture": "x86_64",
          "billingProducts": null,
          "kernelId": null,
          "ramdiskId": null,
          "imageId": "ami-123456",
          "instanceType": "t2.medium",
          "pendingTime": "2015-09-30T05:08:29Z",
          "accountId": "1234567890"
        },
        {
         ...
        }          
    ]
}
```

## Vault config
- Client Policy must be defined before token requester sending requests.
- App-id auth backend is enabled

## API

## `/register-ec2`
**METHOD: POST**

**REQUEST HEADER: `Content-Type:application/json`**

**PARAMETERS: All mandatory**
- `project_id`: String of the project name, e.g: `demo`
- `project_env`: String of the project running envionment, e.g: `production`, `dev`, `qa`
- `pkcs7_sig` : String of the PKCS7 Signature.
> Note that the value of `pkcs7_sig` MAY need to be encoded to be used as URL parameter if it contains characters like `+`

**BODY: The identity document JSON**
```javascript
{
    "devpayProductCodes": null,
    "availabilityZone": "us-west-00",
    "instanceId": "i-abcdefg",
    "region": "us-west-00",
    "privateIp": "172.0.0.0",
    "version": "2010-08-31",
    "architecture": "x86_64",
    "billingProducts": null,
    "kernelId": null,
    "ramdiskId": null,
    "imageId": "ami-123456",
    "instanceType": "t2.medium",
    "pendingTime": "2015-09-30T05:08:29Z",
    "accountId": "1234567890"
}
```


**RESPONSE**
```javascript
{"token": "284a477e-cd93-554b-b0b4-69c5ac24cc82"}
```

## Build and Run
- Install dependency
```bash
cd avocado
sudo pip install -r requirements.txt
```

- Config
Avocado requires following variables to run
  - VAULT_HOST
  - VAULT_TOKEN
  - CONSUL_HOST

- In order to run the application, we'll start it with the built-in server:
```bash
./python avocado.py &
```

## Health check
```bash
curl localhost:5000/Health
{"status": "OK"}
```

## Request example
```bash
curl -X POST -d "$EC2_Identity_DOC_JSON" \
    --header "Content-Type:application/json"  \
    "http://localhost:5000/register-ec2?project_id=demo&project_env=production&pkcs7_sig=$encode_key"
```
> Success resposne
```javascript
{"token": "284a477e-cd93-554b-b0b4-69c5ac24cc82"}
```
> Signature Verification Failure response
```javascript
{"error": "Invalid signature"}
```
> Registration Failure response
```javascript
{"message": "Your registration is failed due to duplication. Please double check your registration info is unique"}
```
