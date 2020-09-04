from oso import Oso
from flask_oso import FlaskOso

from document import Document
import user
from user import User


def init_oso(app):
    """ set up the `Oso` and `FlaskOso` objects, and add them to the global `app` instance."""
    oso = Oso()
    oso.register_class(Document)
    oso.register_class(User)
    oso.load_file("authorization.polar")

    flask_oso = FlaskOso(app=app, oso=oso)
    flask_oso.set_get_actor(user.get_current_user)

    app.oso = oso
    app.flask_oso = flask_oso