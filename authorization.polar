allow(actor: User, "GET", doc: Document) if
    actor.team.lower() in doc.teams;