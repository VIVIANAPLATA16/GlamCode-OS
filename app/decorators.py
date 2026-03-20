from functools import wraps

from flask import redirect, session, url_for


def login_required(view_func):
    """Redirige a login si el usuario no está autenticado."""

    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapped_view

