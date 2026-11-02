from app.models import Game, Player, PlayerSession, Score
from app.models.base import Base


def test_all_models_are_registered():
    assert set(Base.metadata.tables) == {
        "games",
        "players",
        "player_sessions",
        "scores",
    }


def test_game_schema():
    table = Game.__table__

    assert table.c.id.primary_key
    assert table.c.slug.unique
    assert table.c.name.nullable is False
    assert table.c.is_active.nullable is False


def test_player_schema():
    table = Player.__table__

    assert table.c.id.primary_key
    assert table.c.display_name.nullable is False

    indexes = {
        index.name: index
        for index in table.indexes
    }

    assert "ix_players_display_name_lower" in indexes
    assert indexes["ix_players_display_name_lower"].unique


def test_player_session_schema():
    table = PlayerSession.__table__

    assert table.c.id.primary_key
    assert table.c.player_id.nullable is False
    assert table.c.token_hash.unique
    assert table.c.expires_at.nullable is False
    assert table.c.revoked_at.nullable is True


def test_score_schema():
    table = Score.__table__

    assert table.c.id.primary_key
    assert table.c.player_id.nullable is False
    assert table.c.game_id.nullable is False
    assert table.c.data.nullable is False
    assert table.c.ranking_value.nullable is False
    assert table.c.expires_at.nullable is False
    assert table.c.archived_at.nullable is True

    assert table.c.data.type.__class__.__name__ == "JSONB"


def test_model_relationships():
    assert set(Game.__mapper__.relationships.keys()) == {"scores"}
    assert set(Player.__mapper__.relationships.keys()) == {
        "sessions",
        "scores",
    }
    assert set(PlayerSession.__mapper__.relationships.keys()) == {
        "player",
    }
    assert set(Score.__mapper__.relationships.keys()) == {
        "player",
        "game",
    }
