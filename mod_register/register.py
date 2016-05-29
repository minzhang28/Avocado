import requests, base64, json
import config


def is_valid(url_parameter):
    if url_parameter is not None and len(url_parameter) > 0:
        return True
    else:
        return False


def register_on_consul(project_name, project_env, instance_id, mac_address):
    req_endpoint = config.CONSUL_HOST + config.CONSUL_KV_ENDPOINT + "/" + project_name + "/" + project_env
    register_info = dict(instance_id=instance_id, mac_addr=mac_address)

    failure_response = dict(
        message="Your registration is failed due to duplication. Please double check your registration info is unique")
    consul_check_failure_response = dict(message="No key value pair available on consul path:" + req_endpoint)

    try:
        response = requests.get(req_endpoint)
        consul_kv_response = dict(response.json()[0])

        if consul_kv_response.get("Value"):
            project_policy = dict(json.loads(base64.decodestring(consul_kv_response.get("Value"))))
            project_instances = project_policy.get("instances")
            vault_policy_name = project_policy.get("policy")

            # generate project app id if it's not available
            if not is_valid(project_policy.get("app_id")):
                project_policy["app_id"] = project_name + "_" + project_env

            if project_instances is not None:
                if len(project_instances) == 0:
                    project_instances.append(register_info)
                    project_policy["instances"] = project_instances
                    return json.dumps(project_policy)
                else:
                    # if the instance id and mac address is registered already, do nothing
                    if register_info in project_instances:
                        return json.dumps(failure_response)
                    # if the instance mac address is registered already, do nothing
                    else:
                        for i in project_instances:
                            if dict(i)["mac_addr"] == mac_address:
                                return json.dumps(failure_response)
                                break
                    # update project policy if the instance is not registered before
                    project_instances.append(register_info)
                    project_policy["instances"] = project_instances

                    _update_policy_to_consul(req_endpoint, project_policy)
                    return json.dumps(generate_app_id_token(vault_policy_name, project_policy["app_id"], instance_id))
            else:
                project_policy["instances"] = []
                project_policy["instances"].append(register_info)
                _update_policy_to_consul(req_endpoint, project_policy)
                return json.dumps(generate_app_id_token(vault_policy_name, project_policy["app_id"], instance_id))
        else:
            return json.dumps(consul_check_failure_response)

    except Exception as e:
        return json.dumps(dict(error=e.message))


def generate_app_id_token(policy_name, app_id, user_id):
    """
    Generating vault token by talking to the app-id auth backend
    :param policy_name: vault policy name applied to the token
    :param app_id: app id to register
    :param user_id: user id to register
    :return: Vault token
    """

    headers = {'X-Vault-Token': config.VAULT_TOKEN}

    # register app id
    app_id_req_url = config.VAULT_HOST + config.VAULT_APP_ID_MAP_ENDPOINT + "/" + app_id
    app_id_req_body = dict(value=policy_name, display_name=app_id)
    requests.post(app_id_req_url, json.dumps(app_id_req_body), headers=headers)

    # register user id
    user_id_req_url = config.VAULT_HOST + config.VAULT_USER_ID_MAP_ENDPOINT + "/" + user_id
    user_id_req_body = dict(value=app_id)
    requests.post(user_id_req_url, json.dumps(user_id_req_body), headers=headers)

    # generate token
    token_req_url = config.VAULT_HOST + config.VAULT_APP_ID_LOGIN_ENDPOINT
    token_req_body = dict(app_id=app_id, user_id=user_id)
    response = requests.post(token_req_url, json.dumps(token_req_body), headers=headers)
    return dict(token=dict(response.json())["auth"]["client_token"])

def _update_policy_to_consul(req_endpoint, project_policy):
    requests.put(req_endpoint, json.dumps(project_policy))
