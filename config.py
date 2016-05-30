import os

# Consul Config
CONSUL_HOST = os.getenv("CONSUL_HOST", "http://localhost:8500")
CONSUL_KV_ENDPOINT = "/v1/kv"

# Vault Config
VAULT_HOST = os.getenv("VAULT_HOST", "http://localhost:8200")
VAULT_TOKEN = os.getenv("VAULT_TOKEN", "8f33b189-8664-1eec-fa7c-3bce8849907e")
VAULT_APP_ID_MAP_ENDPOINT = "/v1/auth/app-id/map/app-id"
VAULT_USER_ID_MAP_ENDPOINT = "/v1/auth/app-id/map/user-id"
VAULT_APP_ID_LOGIN_ENDPOINT = "/v1/auth/app-id/login"


APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')