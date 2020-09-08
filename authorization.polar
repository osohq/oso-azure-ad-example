allow(actor: User, "GET", doc: Document) if
    group in actor.groups() and
    group.lower() in doc.groups;