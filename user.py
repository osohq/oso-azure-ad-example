import json
from flask import session, Blueprint, render_template
import requests

import app

# Blueprint for users
bp = Blueprint("user", __name__)


class User:
    def __init__(self, id_token_claims):
        self.display_name = id_token_claims.get("name")
        self.first_name = id_token_claims.get("given_name")
        self.surname = id_token_claims.get("family_name")
        self.emails = id_token_claims.get("emails")
        self.country = id_token_claims.get("country")
        self.postal_code = id_token_claims.get("postalCode")
        self.job_title = id_token_claims.get("jobTitle")
        self.team = id_token_claims.get("extension_Team")
        self.organization = id_token_claims.get("extension_Organization")
        self.id = id_token_claims.get("oid")

    def groups(self):
        token = app._get_access_token()
        id = session.get("user").id
        groups = requests.post(
            f"https://graph.microsoft.com/v1.0/users/{id}/getMemberGroups",
            headers={"Authorization": "Bearer " + token},
            json={"securityEnabledOnly": "false"},
        ).json()
        group_data = []
        if groups.get("value"):
            for id in groups.get("value"):
                group_data.append(
                    requests.get(
                        f"https://graph.microsoft.com/v1.0/groups/{id}",
                        headers={"Authorization": "Bearer " + token},
                    )
                    .json()
                    .get("displayName")
                )
        return group_data

    def manager(self):
        token = app._get_access_token()
        id = session.get("user").id
        manager = (
            requests.get(
                f"https://graph.microsoft.com/v1.0/users/{id}/manager",
                headers={"Authorization": "Bearer " + token},
            )
            .json()
            .get("displayName")
        )
        return manager


@bp.route("/groups")
def getGroups():
    group_data = app.get_actor().groups()
    return render_template("display.html", result=json.dumps(group_data))