from __future__ import annotations

import pytest

from app.bootstrap import AppContext
from app.models.user_profile import UserProfile


def test_user_profile_model():
    p = UserProfile(name="Alfando")
    assert p.name == "Alfando"
    assert p.id == 1
    assert p.created_at != ""
    assert p.updated_at != ""

    # Empty name becomes None
    p_empty = UserProfile(name="   ")
    assert p_empty.name is None


def test_user_profile_repository(app_context: AppContext):
    repo = app_context.user_profile_repo

    # Initially seeded with None
    assert repo.get_user_name() is None

    # Set name
    saved = repo.set_user_name("Alfando")
    assert saved == "Alfando"
    assert repo.get_user_name() == "Alfando"

    # Update name
    updated = repo.set_user_name("AlfandoXeon")
    assert updated == "AlfandoXeon"
    assert repo.get_user_name() == "AlfandoXeon"

    # Reject empty name
    with pytest.raises(ValueError):
        repo.set_user_name("   ")
