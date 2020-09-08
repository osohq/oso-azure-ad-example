from dataclasses import dataclass
from flask import g, render_template, Blueprint, current_app


# Blueprint for documents
bp = Blueprint("document", __name__)


@dataclass
class Document:
    id: int
    name: str
    groups: list


def find_by_id(id):
    return DOCUMENTS.get(id)


DOCUMENTS = {
    1: Document(id=1, name="roadmap", groups=["admin", "engineering"]),
    2: Document(id=2, name="customer_list", groups=["admin", "marketing"]),
}


@bp.route("/docs", methods=["GET"])
def index():
    return render_template("doc_index.html", docs=DOCUMENTS)


@bp.route("/docs/<int:id>", methods=["GET"])
def get_doc(id):
    doc = find_by_id(id)
    current_app.flask_oso.authorize(resource=doc)
    return str(doc)