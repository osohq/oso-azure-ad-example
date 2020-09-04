import json
from flask import session, Blueprint, render_template
from requests_oauthlib import OAuth2Session

from msal_auth import get_access_token
from app_config import GRAPH_URL


# Blueprint for users
bp = Blueprint("user", __name__, url_prefix="/user")


class User:
    def __init__(self, id_token_claims):
        self.id = id_token_claims.get("oid")
        self.display_name = id_token_claims.get("name")
        self.first_name = id_token_claims.get("given_name")
        self.surname = id_token_claims.get("family_name")
        self.emails = id_token_claims.get("emails")
        self.job_title = id_token_claims.get("jobTitle")

    def groups(self):
        graph_client = OAuth2Session(token=get_access_token())

        # Get user's groups
        groups = graph_client.post(
            f"{GRAPH_URL}/users/{self.id}/getMemberGroups",
            json={"securityEnabledOnly": "false"},
        ).json()

        # Get group names
        if groups.get("value"):
            return [
                graph_client.get(
                    f"{GRAPH_URL}/groups/{id}",
                )
                .json()
                .get("displayName")
                for id in groups.get("value")
            ]
        elif groups.get("error"):
            return [groups]

    def manager(self):
        graph_client = OAuth2Session(token=get_access_token())
        manager = (
            graph_client.get(
                f"https://graph.microsoft.com/v1.0/users/{self.id}/manager",
            )
            .json()
            .get("displayName")
        )
        return manager


def get_current_user():
    return session.get("user")


@bp.route("/groups")
def get_groups():
    group_data = get_current_user().groups()
    return render_template(
        "display.html", result=json.dumps(group_data), title="My Groups"
    )


@bp.route("/manager")
def get_manager():
    manager = get_current_user().manager()
    return render_template("display.html", result=manager, title="My Manager")