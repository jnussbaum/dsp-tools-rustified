import re
from dataclasses import dataclass
from pathlib import Path
from test.unittests.commands.xmlupload.connection_mock import ConnectionMockBase
from typing import Any, ClassVar

import pytest
from lxml import etree

from dsp_tools.commands.xmlupload.check_consistency_with_ontology import do_xml_consistency_check
from dsp_tools.commands.xmlupload.ontology_client import OntologyClientLive
from dsp_tools.models.exceptions import BaseError, UserError


@dataclass
class ConnectionMockRaising(ConnectionMockBase):
    def get(
        self,
        route: str,  # noqa: ARG002 (unused-method-argument)
        headers: dict[str, str] | None = None,  # noqa: ARG002 (unused-method-argument)
    ) -> dict[str, Any]:
        raise BaseError("foo")


@dataclass
class ConnectionMockWithResponses(ConnectionMockBase):
    get_responses: ClassVar[list[dict[str, Any]]] = [
        {
            "project": {
                "ontologies": ["/testonto"],
            }
        },
        {
            "@graph": [
                {
                    "@id": "testonto:ValidResourceClass",
                    "knora-api:isResourceClass": True,
                }
            ]
        },
        {
            "@graph": [
                {
                    "@id": "knora-api:ValidResourceClass",
                    "knora-api:isResourceClass": True,
                }
            ]
        },
    ]

    def get(
        self,
        route: str,  # noqa: ARG002 (unused-method-argument)
        headers: dict[str, str] | None = None,  # noqa: ARG002 (unused-method-argument)
    ) -> dict[str, Any]:
        return self.get_responses.pop(0)


def test_error_on_nonexistent_shortcode() -> None:
    root = etree.parse("testdata/xml-data/test-data-minimal.xml").getroot()
    con = ConnectionMockRaising()
    ontology_client = OntologyClientLive(
        con=con,
        shortcode="9999",
        default_ontology="foo",
        save_location=Path("bar"),
    )
    with pytest.raises(UserError, match="A project with shortcode 9999 could not be found on the DSP server"):
        do_xml_consistency_check(ontology_client, root)


def test_error_on_nonexistent_onto_name() -> None:
    root = etree.fromstring(
        '<knora shortcode="4124" default-ontology="notexistingfantasyonto">'
        '<resource label="The only resource" restype=":minimalResource" id="the_only_resource"/>'
        "</knora>"
    )
    con = ConnectionMockWithResponses()
    ontology_client = OntologyClientLive(
        con=con,
        shortcode="4124",
        default_ontology="notexistingfantasyonto",
        save_location=Path("bar"),
    )
    expected = re.escape(
        "\nSome property and/or class type(s) used in the XML are unknown.\n"
        "The ontologies for your project on the server are:\n"
        "    - testonto\n"
        "    - knora-api\n\n"
        "---------------------------------------\n\n"
        "The following resource(s) have an invalid resource type:\n\n"
        "    Resource Type: ':minimalResource'\n"
        "    Problem: 'Unknown ontology prefix'\n"
        "    Resource ID(s):\n"
        "    - the_only_resource\n\n"
        "---------------------------------------\n\n"
    )
    with pytest.raises(UserError, match=expected):
        do_xml_consistency_check(ontology_client, root)


if __name__ == "__main__":
    pytest.main([__file__])