from dataclasses import dataclass
from flask import g, render_template, Blueprint, current_app, request

from flask_oso import authorize


# Blueprint for documents
bp = Blueprint("document", __name__)


@dataclass
class Document:
    id: int
    owner_id: str
    groups: list
    is_private: bool
    content: str


def find_by_id(id):
    return DOCUMENTS.get(id)


DOCUMENTS = {
    1: Document(
        id=1,
        owner_id="5890e32a-c2ac-4aa0-902d-0717017d1bc3",
        groups=["engineering"],
        is_private=True,
        content="This is a private engineering doc.",
    ),
    2: Document(
        id=2,
        owner_id="273dd85f-0728-44c0-8588-c130f39c900b",
        groups=["marketing"],
        is_private=True,
        content="This is a private marketing doc.",
    ),
    3: Document(
        id=3,
        owner_id="273dd85f-0728-44c0-8588-c130f39c900b",
        groups=["admin"],
        is_private=False,
        content="This is a public admin doc.",
    ),
}


@authorize(resource=request)
@bp.route("/docs", methods=["GET"])
def index():
    return render_template("doc_index.html", docs=DOCUMENTS)


@bp.route("/docs/<int:id>", methods=["GET"])
def get_doc(id):
    doc = find_by_id(id)
    current_app.flask_oso.authorize(resource=doc)
    return doc.content