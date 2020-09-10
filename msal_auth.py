from flask import url_for, Blueprint, request, redirect, render_template, session
import uuid
import msal

import app_config


def get_access_token():
    """ Get an access token for the MS Graph API"""
    result = build_msal_app(
        authority="https://login.microsoftonline.com/52c9ac72-820e-4183-9ee8-92567f2752aa",
    ).acquire_token_for_client(
        scopes=app_config.SCOPE,  # Misspelled scope would cause an HTTP 400 error here
    )
    return result["access_token"]


def build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID,
        authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET,
    )


def build_auth_url(authority=None, scopes=None, state=None):
    return build_msal_app(authority=authority).get_authorization_request_url(
        scopes or [],
        state=state or str(uuid.uuid4()),
        redirect_uri=url_for("authorized", _external=True),
    )
