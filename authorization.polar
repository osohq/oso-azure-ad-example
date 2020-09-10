# allow anyone to get public documents
allow(_actor: User, "GET", doc: Document) if
    not doc.is_private;

# allow the CEO to view any document
allow(actor: User, "GET", _doc: Document) if
    actor.job_title = "CEO";

# allow users to view their own docs
allow(actor: User, "GET", doc: Document) if
    actor.id = doc.owner_id;

# allow users to view documents in their group
allow(actor: User, "GET", doc: Document) if
    group in actor.groups() and
    group.lower() in doc.groups;