import json
import uuid
import requests
from flask import Flask, render_template, session, request, redirect, url_for, g
from flask_session import Session  # https://pythonhosted.org/Flask-Session
import msal
import app_config
from oso import Oso
from flask_oso import FlaskOso
from werkzeug.middleware.proxy_fix import ProxyFix

import document
from document import Document
import user
from user import User

# setup oso
def get_actor():
    return session.get("user")


def init_oso(app):
    oso = Oso()
    flask_oso = FlaskOso(app=app, oso=oso)
    oso.register_class(Document)
    oso.register_class(User)
    oso.load_file("authorization.polar")

    flask_oso.set_get_actor(get_actor)

    app.oso = oso
    app.flask_oso = flask_oso


def create_app():
    app = Flask(__name__)
    app.config.from_object(app_config)
    Session(app)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    init_oso(app)

    app.jinja_env.globals.update(_build_auth_url=_build_auth_url)  # Used in template

    @app.route("/")
    def index():
        if not session.get("user"):
            return redirect(url_for("login"))
        user = session.get("user")
        return render_template("index.html", user=user, version=msal.__version__)

    @app.route("/login")
    def login():
        session["state"] = str(uuid.uuid4())
        # Technically we could use empty list [] as scopes to do just sign in,
        # here we choose to also collect end user consent upfront
        auth_url = _build_auth_url(scopes=[], state=session["state"])
        return render_template(
            "login.html", auth_url=auth_url, version=msal.__version__
        )

    @app.route(
        app_config.REDIRECT_PATH
    )  # Its absolute URL must match your app's redirect_uri set in AAD
    def authorized():
        if request.args.get("state") != session.get("state"):
            return redirect(url_for("index"))  # No-OP. Goes back to Index page
        if "error" in request.args:  # Authentication/Authorization failure
            return render_template("auth_error.html", result=request.args)
        if request.args.get("code"):
            cache = _load_cache()
            id_token_result = _build_msal_app(
                cache=cache
            ).acquire_token_by_authorization_code(
                request.args["code"],
                redirect_uri=url_for("authorized", _external=True),
                scopes=[],
            )
            if "error" in id_token_result:
                return render_template("auth_error.html", result=id_token_result)
            print(id_token_result)
            user = User(id_token_result.get("id_token_claims"))
            session["user"] = user
            _save_cache(cache)

            # get the access token for the graph api and store it
            _get_access_token()

        return redirect(url_for("index"))

    @app.route("/logout")
    def logout():
        session.clear()  # Wipe out user and its token cache from session
        return redirect(  # Also logout from your tenant's web session
            app_config.AUTHORITY
            + "/oauth2/v2.0/logout"
            + "?post_logout_redirect_uri="
            + url_for("index", _external=True)
        )

    @app.route("/graphcall")
    def graphcall():
        token = _get_access_token()
        if not token:
            return redirect(url_for("login"))
        graph_data = requests.get(  # Use token to call downstream service
            app_config.ENDPOINT,
            headers={"Authorization": "Bearer " + token},
        ).json()
        return render_template("display.html", result=graph_data)

    app.register_blueprint(document.bp)
    app.register_blueprint(user.bp)
    return app


def _get_access_token():
    if not session.get("access_token"):
        result = _build_msal_app(
            authority="https://login.microsoftonline.com/52c9ac72-820e-4183-9ee8-92567f2752aa",
        ).acquire_token_for_client(
            scopes=app_config.SCOPE,  # Misspelled scope would cause an HTTP 400 error here
        )
        print(result)
        session["access_token"] = result["access_token"]

    return session.get("access_token")


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID,
        authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET,
        token_cache=cache,
    )


def _build_auth_url(authority=None, scopes=None, state=None):
    return _build_msal_app(authority=authority).get_authorization_request_url(
        scopes or [],
        state=state or str(uuid.uuid4()),
        redirect_uri=url_for("authorized", _external=True),
    )


def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result
