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