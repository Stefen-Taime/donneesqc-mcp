"""Tests pour la validation SQL (lecture seule)."""

import pytest

from helpers.ckan_api import validate_sql


class TestValidateSQL:
    """Vérifie que seules les requêtes SELECT passent."""

    def test_select_simple(self):
        validate_sql('SELECT * FROM "abc-123"')

    def test_select_with_where(self):
        validate_sql('SELECT "ville", COUNT(*) FROM "r1" WHERE "annee" = 2024 GROUP BY "ville"')

    def test_select_with_semicolon(self):
        validate_sql('SELECT * FROM "r1";')

    def test_select_with_whitespace(self):
        validate_sql('  SELECT * FROM "r1"  ')

    def test_select_lowercase(self):
        validate_sql('select * from "r1"')

    def test_select_with_subquery(self):
        validate_sql('SELECT * FROM (SELECT "a" FROM "r1") sub')

    def test_insert_rejected(self):
        with pytest.raises(ValueError, match="instructions interdites"):
            validate_sql('SELECT 1; INSERT INTO "r1" VALUES (1)')

    def test_update_rejected(self):
        with pytest.raises(ValueError, match="instructions interdites"):
            validate_sql('SELECT 1; UPDATE "r1" SET x = 1')

    def test_delete_rejected(self):
        with pytest.raises(ValueError, match="instructions interdites"):
            validate_sql('SELECT 1; DELETE FROM "r1"')

    def test_drop_rejected(self):
        with pytest.raises(ValueError, match="instructions interdites"):
            validate_sql('SELECT 1; DROP TABLE "r1"')

    def test_truncate_rejected(self):
        with pytest.raises(ValueError, match="instructions interdites"):
            validate_sql('SELECT 1; TRUNCATE "r1"')

    def test_alter_rejected(self):
        with pytest.raises(ValueError, match="instructions interdites"):
            validate_sql('SELECT 1; ALTER TABLE "r1" ADD COLUMN x INT')

    def test_create_rejected(self):
        with pytest.raises(ValueError, match="instructions interdites"):
            validate_sql('SELECT 1; CREATE TABLE evil (x INT)')

    def test_not_starting_with_select(self):
        with pytest.raises(ValueError, match="SELECT"):
            validate_sql('INSERT INTO "r1" VALUES (1)')

    def test_empty_string(self):
        with pytest.raises(ValueError, match="SELECT"):
            validate_sql("")

    def test_grant_rejected(self):
        with pytest.raises(ValueError, match="instructions interdites"):
            validate_sql("SELECT 1; GRANT ALL ON r1 TO public")

    def test_exec_rejected(self):
        with pytest.raises(ValueError, match="instructions interdites"):
            validate_sql("SELECT 1; EXEC sp_evil")
