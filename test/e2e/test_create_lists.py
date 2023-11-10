# pylint: disable=missing-class-docstring

import json
import unittest
from pathlib import Path

import jsonpath_ng.ext

from dsp_tools.utils.project_create import create_project
from dsp_tools.utils.project_create_lists import create_lists


class TestCreateLists(unittest.TestCase):
    server = "http://0.0.0.0:3333"
    user = "root@example.com"
    password = "test"
    test_project_minimal_file = Path("testdata/json-project/test-project-minimal.json")

    def test_create_lists(self) -> None:
        """
        Test that the 'lists' section of a JSON file is correctly created,
        and that the returned {node name: iri} mapping contains the same node names than the original list.
        """
        # create a project without lists
        # (if it was already created in a previous test, the function returns False, which doesn't matter)
        create_project(
            project_file_as_path_or_parsed=self.test_project_minimal_file.absolute(),
            server=self.server,
            user_mail=self.user,
            password=self.password,
            verbose=True,
        )

        # insert a "lists" section into the project that was created
        with open("testdata/excel2json/lists-multilingual-output-expected.json", encoding="utf-8") as f:
            lists_section = json.load(f)
        with open(self.test_project_minimal_file, encoding="utf-8") as f:
            test_project_minimal = json.load(f)
        test_project_minimal["project"]["lists"] = [lists_section[0]]

        # The method to be tested can now be called with the project with the added list
        name2iri_mapping, success = create_lists(
            server=self.server,
            user=self.user,
            password=self.password,
            project_file_as_path_or_parsed=test_project_minimal,
        )

        # test if the returned mapping contains the same node names than the original list
        self.assertTrue(success)
        names_returned = [str(m.path) for m in jsonpath_ng.ext.parse("$..* where id").find(name2iri_mapping)]
        node_names = [m.value for m in jsonpath_ng.ext.parse("$.project.lists[*]..name").find(test_project_minimal)]
        self.assertListEqual(names_returned, node_names)