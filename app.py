from flask import Flask, render_template, redirect, url_for, request, session
from flask_session import Session  # https://pythonhosted.org/Flask-Session
import msal
import app_config
from flask_oso import FlaskOso
from werkzeug.middleware.proxy_fix import ProxyFix
import uuid

import document
import user
from user import get_current_user, User
from oso_auth import init_oso
import msal_auth
from msal_auth import build_auth_url, build_msal_app, get_access_token


def create_app():
    app = Flask(__name__)
    app.config.from_object(app_config)
    Session(app)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # initialize oso auth
    init_oso(app)

    app.jinja_env.globals.update(_build_auth_url=build_auth_url)  # Used in template

    @app.route("/")
    def index():
        if not get_current_user():
            return redirect(url_for("login"))
        user = get_current_user()
        return render_template("index.html", user=user, version=msal.__version__)

    @app.route("/login")
    def login():
        session["state"] = str(uuid.uuid4())
        # Technically we could use empty list [] as scopes to do just sign in,
        # here we choose to also collect end user consent upfront
        auth_url = build_auth_url(scopes=[], state=session["state"])
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
            id_token_result = build_msal_app().acquire_token_by_authorization_code(
                request.args["code"],
                redirect_uri=url_for("authorized", _external=True),
                scopes=[],
            )
            if "error" in id_token_result:
                return render_template("auth_error.html", result=id_token_result)
            print(id_token_result)
            user = User(id_token_result.get("id_token_claims"))
            session["user"] = user

            # get the access token for the graph api and store it
            get_access_token()

        return redirect(url_for("index"))

    @app.route("/logout")
    def logout():
        session.clear()  # Wipe out user from session
        return redirect(  # Also logout from your tenant's web session
            app_config.AUTHORITY
            + "/oauth2/v2.0/logout"
            + "?post_logout_redirect_uri="
            + url_for("index", _external=True)
        )

    # register Blueprints
    app.register_blueprint(document.bp)
    app.register_blueprint(user.bp)

    return app
