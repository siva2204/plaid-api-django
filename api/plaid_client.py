import plaid
from plaid.api import plaid_api

# Available environments are
# 'Production'
# 'Development'
# 'Sandbox'
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': "635b53e28e27a300134ff3c8",
        'secret': "c2fe779b96bb318c4d3c051114c494",
    }
)

api_client = plaid.ApiClient(configuration)
plaid_client = plaid_api.PlaidApi(api_client)
