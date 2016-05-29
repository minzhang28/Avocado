import os

# Consul Config
CONSUL_HOST = os.getenv("CONSUL_HOST", "http://localhost:8500")
CONSUL_KV_ENDPOINT = "/v1/kv"

# Vault Config
VAULT_HOST = os.getenv("VAULT_HOST", "http://localhost:8200")
VAULT_TOKEN = os.getenv("VAULT_TOKEN", "6af1131c-4c3c-0ce6-3cc8-f22af8747524")
VAULT_APP_ID_MAP_ENDPOINT = "/v1/auth/app-id/map/app-id"
VAULT_USER_ID_MAP_ENDPOINT = "/v1/auth/app-id/map/user-id"
VAULT_APP_ID_LOGIN_ENDPOINT = "/v1/auth/app-id/login"
