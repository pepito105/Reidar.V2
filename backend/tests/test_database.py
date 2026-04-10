import inspect


def test_get_db_is_async_generator():
    """get_db must be an async generator for use with FastAPI Depends()."""
    from app.core.database import get_db
    assert inspect.isasyncgenfunction(get_db)


def test_engine_exists():
    """Module-level engine must be created on import."""
    from app.core.database import engine
    assert engine is not None


def test_async_session_local_exists():
    """AsyncSessionLocal factory must be available on import."""
    from app.core.database import AsyncSessionLocal
    assert AsyncSessionLocal is not None


def test_base_has_metadata():
    """Base must be a declarative base with metadata for Alembic."""
    from app.core.database import Base
    assert hasattr(Base, "metadata")
    assert hasattr(Base, "registry")


def test_create_vector_extension_is_coroutine():
    """create_vector_extension must be an async function."""
    from app.core.database import create_vector_extension
    assert inspect.iscoroutinefunction(create_vector_extension)
