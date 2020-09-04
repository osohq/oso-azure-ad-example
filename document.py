from dataclasses import dataclass


@dataclass
class Document:
    id: int
    name: str
    teams: list


def find_by_id(id):
    return DOCUMENTS.get(id)


DOCUMENTS = {
    1: Document(id=1, name="roadmap", teams=["admin", "engineering"]),
    2: Document(id=2, name="customer_list", teams=["admin", "marketing"]),
}