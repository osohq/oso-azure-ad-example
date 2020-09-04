class User:
    def __init__(self, id_token_claims):
        self.display_name = id_token_claims["name"]
        self.first_name = id_token_claims["given_name"]
        self.surname = id_token_claims["family_name"]
        self.emails = id_token_claims["emails"]
        self.country = id_token_claims["country"]
        self.postal_code = id_token_claims["postalCode"]
        self.job_title = id_token_claims["jobTitle"]
        self.team = id_token_claims["extension_Team"]
        self.organization = id_token_claims["extension_Organization"]