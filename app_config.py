import os

b2c_tenant = "ososecurity"
signupsignin_user_flow = "B2C_1_signupsignin1"
editprofile_user_flow = "B2C_1_profileediting1"
resetpassword_user_flow = "B2C_1_passwordreset1"
authority_template = (
    "https://{tenant}.b2clogin.com/{tenant}.onmicrosoft.com/{user_flow}"
)

CLIENT_ID = "e129429e-5788-482a-8185-c1db5a97d8b4"  # Application (client) ID of app registration

CLIENT_SECRET = (
    "_Ntp2wy_~oE3M~cE6n5OYJH69j99nYHDME"  # Placeholder - for use ONLY during testing.
)

# In a production app, we recommend you use a more secure method of storing your secret,
# like Azure Key Vault. Or, use an environment variable as described in Flask's documentation:
# https://flask.palletsprojects.com/en/1.1.x/config/#configuring-from-environment-variables
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# if not CLIENT_SECRET:
#     raise ValueError("Need to define CLIENT_SECRET environment variable")

AUTHORITY = authority_template.format(
    tenant=b2c_tenant, user_flow=signupsignin_user_flow
)
B2C_PROFILE_AUTHORITY = authority_template.format(
    tenant=b2c_tenant, user_flow=editprofile_user_flow
)
B2C_RESET_PASSWORD_AUTHORITY = authority_template.format(
    tenant=b2c_tenant, user_flow=resetpassword_user_flow
)

REDIRECT_PATH = "/getAToken"  # Used for forming an absolute URL to your redirect URI.
# The absolute URL must match the redirect URI you set
# in the app's registration in the Azure portal.

# You can find more Microsoft Graph API endpoints from Graph Explorer
# https://developer.microsoft.com/en-us/graph/graph-explorer
GRAPH_URL = (
    "https://graph.microsoft.com/v1.0"
)

# You can find the proper permission names from this document
# https://docs.microsoft.com/en-us/graph/permissions-reference
SCOPE = ["https://graph.microsoft.com/.default"]

SESSION_TYPE = (
    "filesystem"  # Specifies the token cache should be stored in server-side session
)
