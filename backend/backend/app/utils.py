from sqlalchemy import inspect


def to_dict(obj, exclude: set | None = None) -> dict | None:
    """Converts one SQLAlchemy model instance into a plain JSON-serializable dict.
    FastAPI's default response encoding does not introspect ORM objects on
    its own — returning one directly silently serializes to {}. Every router
    that returns a model instance (or a list of them) should pass through
    this, or through to_dict_list for collections.
    Pass `exclude` for any column that should never leave the server, such
    as a hashed credential — a listing endpoint should never echo a hash
    field, even a one-way one."""
    if obj is None:
        return None
    exclude = exclude or set()
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs if c.key not in exclude}


def to_dict_list(objs, exclude: set | None = None) -> list[dict]:
    return [to_dict(o, exclude=exclude) for o in objs]
