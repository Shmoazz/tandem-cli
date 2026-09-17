"""Unit tests for tandem, standard library unittest only: `python3 -m unittest -q tandem_test`.

Only the pure decisions are covered, which is all of them that can be wrong in an
interesting way; the argparse wiring and the urlopen calls carry no test on purpose.
The CLI has no .py extension, so it is loaded by path rather than imported.
"""
import importlib.util
import os
import unittest
from importlib.machinery import SourceFileLoader

_LOADER = SourceFileLoader("tandem", os.path.join(os.path.dirname(os.path.abspath(__file__)), "tandem"))
tandem = importlib.util.module_from_spec(importlib.util.spec_from_loader("tandem", _LOADER))
_LOADER.exec_module(tandem)


class NormalizeStatus(unittest.TestCase):
    def test_the_ui_wording_becomes_the_api_word(self):
        shown_in_the_web_app = "In Review"

        stored = tandem.normalize_status(shown_in_the_web_app, "draft")

        self.assertEqual(stored, "review")

    def test_a_word_tandem_does_not_know_becomes_the_fallback(self):
        invented = "blocked"

        stored = tandem.normalize_status(invented, "draft")

        self.assertEqual(stored, "draft")


class ChooseTable(unittest.TestCase):
    def test_a_name_matches_whatever_case_it_is_typed_in(self):
        tables = [{"id": "aaa", "name": "Motor Requirements"}, {"id": "bbb", "name": "Frame"}]

        table = tandem.choose_table(tables, "motor requirements")

        self.assertEqual(table["id"], "aaa")

    def test_a_uuid_matches_too(self):
        tables = [{"id": "aaa", "name": "Motor Requirements"}, {"id": "bbb", "name": "Frame"}]

        table = tandem.choose_table(tables, "bbb")

        self.assertEqual(table["name"], "Frame")

    def test_one_table_needs_no_flag(self):
        tables = [{"id": "aaa", "name": "Motor Requirements"}]

        table = tandem.choose_table(tables, None)

        self.assertEqual(table["id"], "aaa")

    def test_several_tables_and_no_flag_lists_the_choices(self):
        tables = [{"id": "aaa", "name": "Motor Requirements"}, {"id": "bbb", "name": "Frame"}]

        with self.assertRaises(SystemExit) as stop:
            tandem.choose_table(tables, None)

        self.assertIn("pick one with -t: Motor Requirements, Frame", str(stop.exception))

    def test_a_name_that_is_not_there_lists_the_ones_that_are(self):
        tables = [{"id": "aaa", "name": "Motor Requirements"}]

        with self.assertRaises(SystemExit) as stop:
            tandem.choose_table(tables, "Frame")

        self.assertIn("No table named 'Frame'. Tables: Motor Requirements", str(stop.exception))


class ChooseProgram(unittest.TestCase):
    def test_the_flag_beats_the_environment_and_the_tab(self):
        flag, env, tab = "from-flag", "from-env", "from-tab"

        program = tandem.choose_program(flag, env, tab)

        self.assertEqual(program, "from-flag")

    def test_the_environment_beats_the_tab(self):
        env, tab = "from-env", "from-tab"

        program = tandem.choose_program(None, env, tab)

        self.assertEqual(program, "from-env")

    def test_an_account_with_one_program_needs_no_flag(self):
        programs = [{"id": "only-one", "name": "Roly Poly"}]

        program = tandem.choose_program(None, None, None, programs)

        self.assertEqual(program, "only-one")

    def test_several_programs_name_themselves_in_the_refusal(self):
        programs = [{"id": "p1", "name": "Roly Poly"}, {"id": "p2", "name": "Elevator"}]

        with self.assertRaises(SystemExit) as stop:
            tandem.choose_program(None, None, None, programs)

        self.assertIn("Roly Poly (p1), Elevator (p2)", str(stop.exception))

    def test_a_chrome_session_with_no_program_says_how_to_name_one(self):
        nothing_named_a_program = (None, None, None)

        with self.assertRaises(SystemExit) as stop:
            tandem.choose_program(*nothing_named_a_program)

        self.assertEqual(str(stop.exception), tandem.NO_PROGRAM)


class AddBody(unittest.TestCase):
    def test_a_status_tandem_does_not_know_is_created_as_a_draft(self):
        existing = {}

        body = tandem.add_body("MT-1", "Torque", "It turns.", "nonsense", "", None, existing, "Motors")

        self.assertEqual(body["status"], "draft")

    def test_a_blank_owner_is_left_off_the_body(self):
        existing = {}

        body = tandem.add_body("MT-1", "Torque", "It turns.", "draft", "", None, existing, "Motors")

        self.assertNotIn("owner", body)

    def test_a_parent_number_is_sent_as_the_parent_id(self):
        existing = {"MT-0": "parent-uuid"}

        body = tandem.add_body("MT-1", "Torque", "It turns.", "draft", "", "MT-0", existing, "Motors")

        self.assertEqual(body["parent_id"], "parent-uuid")

    def test_a_parent_that_is_not_in_the_table_names_the_table(self):
        existing = {"MT-0": "parent-uuid"}

        with self.assertRaises(SystemExit) as stop:
            tandem.add_body("MT-1", "Torque", "It turns.", "draft", "", "MT-9", existing, "Motors")

        self.assertIn("Parent 'MT-9' not found in table Motors", str(stop.exception))


class UpdateBody(unittest.TestCase):
    def test_only_the_flags_that_were_passed_are_sent(self):
        rows = [{"number": "MT-1", "id": "one"}]

        body = tandem.update_body(None, None, "approved", None, None, rows, "Motors")

        self.assertEqual(body, {"status": "approved"})

    def test_unparenting_sends_an_explicit_null(self):
        rows = [{"number": "MT-1", "id": "one"}]

        body = tandem.update_body(None, None, None, None, "none", rows, "Motors")

        self.assertEqual(body, {"parent_id": None})

    def test_a_new_parent_is_looked_up_by_number(self):
        rows = [{"number": "MT-1", "id": "one"}, {"number": "MT-0", "id": "zero"}]

        body = tandem.update_body(None, None, None, None, "MT-0", rows, "Motors")

        self.assertEqual(body, {"parent_id": "zero"})

    def test_a_status_tandem_does_not_know_is_sent_as_typed(self):
        rows = [{"number": "MT-1", "id": "one"}]

        body = tandem.update_body(None, None, "blocked", None, None, rows, "Motors")

        self.assertEqual(body, {"status": "blocked"})

    def test_an_update_with_no_flags_says_which_flags_exist(self):
        rows = [{"number": "MT-1", "id": "one"}]

        with self.assertRaises(SystemExit) as stop:
            tandem.update_body(None, None, None, None, None, rows, "Motors")

        self.assertEqual(str(stop.exception), tandem.NOTHING_TO_UPDATE)


class CsvRowBody(unittest.TestCase):
    def test_a_row_with_no_number_is_nothing_to_create(self):
        row = {"Number": "  ", "Name": "Stray note"}

        body, warning = tandem.csv_row_body(row, "", {})

        self.assertEqual((body, warning), (None, None))

    def test_the_columns_land_in_the_body(self):
        row = {"Number": "MT-1", "Name": "Torque", "Statement": "It turns.", "Status": "Approved"}

        body, _ = tandem.csv_row_body(row, "", {})

        self.assertEqual(body, {"number": "MT-1", "name": "Torque",
                                "statement": "It turns.", "status": "approved"})

    def test_a_row_without_an_owner_takes_the_default(self):
        row = {"Number": "MT-1", "Owner": ""}

        body, _ = tandem.csv_row_body(row, "zach@example.com", {})

        self.assertEqual(body["owner"], "zach@example.com")

    def test_a_parent_already_created_is_sent_as_the_parent_id(self):
        row = {"Number": "MT-1", "Parent": "MT-0"}

        body, warning = tandem.csv_row_body(row, "", {"MT-0": "zero"})

        self.assertEqual((body["parent_id"], warning), ("zero", None))

    def test_a_parent_that_is_not_there_still_creates_the_row(self):
        row = {"Number": "MT-1", "Parent": "MT-9"}

        body, _ = tandem.csv_row_body(row, "", {"MT-0": "zero"})

        self.assertNotIn("parent_id", body)

    def test_a_parent_that_is_not_there_warns_by_number(self):
        row = {"Number": "MT-1", "Parent": "MT-9"}

        _, warning = tandem.csv_row_body(row, "", {"MT-0": "zero"})

        self.assertEqual(warning, "warn: parent MT-9 of MT-1 not found; creating at top level")


class AuthHeaders(unittest.TestCase):
    def test_an_api_key_travels_as_x_api_key(self):
        auth = tandem.Auth(api_key="tk-123")

        headers = auth.headers()

        self.assertEqual(headers, {"X-API-Key": "tk-123"})

    def test_a_cognito_token_travels_as_a_bearer(self):
        auth = tandem.Auth(token="id-token")

        headers = auth.headers()

        self.assertEqual(headers, {"Authorization": "Bearer id-token"})


class ChooseAuth(unittest.TestCase):
    def test_the_environment_beats_the_key_file(self):
        env, key_file = {"TANDEM_API_KEY": "from-env"}, "from-file\n"

        auth = tandem.choose_auth(env, key_file)

        self.assertEqual(auth.api_key, "from-env")

    def test_the_key_is_the_first_line_of_the_file(self):
        key_file = "from-file\n# the trailing notes are not the key\n"

        auth = tandem.choose_auth({}, key_file)

        self.assertEqual(auth.api_key, "from-file")

    def test_no_key_anywhere_means_the_chrome_session(self):
        env, key_file = {"TANDEM_API_KEY": "   "}, None

        auth = tandem.choose_auth(env, key_file)

        self.assertIsNone(auth)


class ResolveAuth(unittest.TestCase):
    def test_a_key_never_reaches_for_chrome(self):
        def grab():
            raise AssertionError("Chrome was asked for a session that a key had already provided")

        auth, tab_program = tandem.resolve_auth({"TANDEM_API_KEY": "tk-123"}, None, grab=grab)

        self.assertEqual((auth.api_key, tab_program), ("tk-123", None))

    def test_a_chrome_session_supplies_the_token_and_the_open_program(self):
        session = ("client-id", "refresh-token", "program-in-the-tab")

        auth, tab_program = tandem.resolve_auth({}, None, grab=lambda: session,
                                                mint=lambda cid, rt: "minted-" + cid)

        self.assertEqual((auth.headers(), tab_program),
                         ({"Authorization": "Bearer minted-client-id"}, "program-in-the-tab"))

    def test_no_key_and_no_tandem_tab_says_what_to_do(self):
        def no_tab():
            return tandem.parse_chrome_session("")

        with self.assertRaises(SystemExit) as stop:
            tandem.resolve_auth({}, None, grab=no_tab)

        self.assertEqual(str(stop.exception), tandem.NO_SESSION)


class Paths(unittest.TestCase):
    def test_requirements_hang_off_their_table(self):
        program, table = "prog-1", "table-1"

        path = tandem.requirements_path(program, table)

        self.assertEqual(path, "/programs/prog-1/req-tables/table-1/requirements")


if __name__ == "__main__":
    unittest.main()
