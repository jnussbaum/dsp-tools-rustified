from dataclasses import dataclass, field
from test.unittests.commands.xmlupload.connection_mock import ConnectionMockBase
from typing import Any
from uuid import uuid4

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.value import FormattedTextValue
from dsp_tools.commands.xmlupload.stash.stash_models import (
    LinkValueStash,
    LinkValueStashItem,
    StandoffStash,
    StandoffStashItem,
    Stash,
)
from dsp_tools.commands.xmlupload.xmlupload import _upload_stash
from dsp_tools.utils.connection import Connection

# ruff: noqa: ARG002 (unused-method-argument)
# ruff: noqa: D102 (undocumented-public-method)


class ProjectClientStub:
    """Stub class for ProjectClient."""

    def get_project_iri(self) -> str:
        raise NotImplementedError("get_project_iri not implemented")

    def get_ontology_iris(self) -> list[str]:
        raise NotImplementedError("get_project_iri not implemented")

    def get_ontology_name_dict(self) -> dict[str, str]:
        return {}

    def get_ontology_iri_dict(self) -> dict[str, str]:
        raise NotImplementedError("get_project_iri not implemented")


@dataclass
class ConnectionMock(ConnectionMockBase):
    """Mock class for Connection."""

    get_responses: list[dict[str, Any]] = field(default_factory=list)
    post_responses: list[dict[str, Any]] = field(default_factory=list)
    put_responses: list[dict[str, Any]] = field(default_factory=list)

    def get(
        self,
        route: str,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return self.get_responses.pop(0)

    def post(
        self,
        route: str,
        data: dict[str, Any] | None = None,
        files: dict[str, tuple[str, Any]] | None = None,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        return self.post_responses.pop(0)

    def put(
        self,
        route: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return self.put_responses.pop(0)


class TestUploadLinkValueStashes:
    def test_upload_link_value_stash(self) -> None:
        """Upload stashed link values (resptr), if all goes well."""
        stash = Stash.make(
            standoff_stash=None,
            link_value_stash=LinkValueStash.make(
                [
                    LinkValueStashItem("001", "sometype", "someprop", "002"),
                ],
            ),
        )
        assert stash
        iri_resolver = IriResolver(
            {
                "001": "http://www.rdfh.ch/0001/001",
                "002": "http://www.rdfh.ch/0001/002",
            }
        )
        con: Connection = ConnectionMock(post_responses=[{}])
        nonapplied = _upload_stash(
            stash=stash,
            iri_resolver=iri_resolver,
            con=con,
            verbose=False,
            project_client=ProjectClientStub(),
        )
        assert nonapplied is None


class TestUploadTextValueStashes:
    def test_upload_text_value_stash(self) -> None:
        """Upload stashed text values (standoff), if all goes well."""
        value_uuid = str(uuid4())
        property_name = "someprop"
        stash = Stash.make(
            standoff_stash=StandoffStash.make(
                [
                    StandoffStashItem(
                        "001", "sometype", value_uuid, property_name, FormattedTextValue("<p>some text</p>")
                    ),
                ]
            ),
            link_value_stash=None,
        )
        assert stash
        iri_resolver = IriResolver(
            {
                "001": "http://www.rdfh.ch/0001/001",
                "002": "http://www.rdfh.ch/0001/002",
            }
        )
        con: Connection = ConnectionMock(
            get_responses=[
                {
                    property_name: [
                        {
                            "@id": "http://www.rdfh.ch/0001/001/values/01",
                            "knora-api:textValueAsXml": "<p>not relevant</p>",
                        },
                        {
                            "@id": "http://www.rdfh.ch/0001/001/values/01",
                            "knora-api:textValueAsXml": f"<p>{value_uuid}</p>",
                        },
                    ],
                    "@context": {},
                },
            ],
            put_responses=[{}],
        )
        nonapplied = _upload_stash(
            stash=stash,
            iri_resolver=iri_resolver,
            con=con,
            verbose=False,
            project_client=ProjectClientStub(),
        )
        assert nonapplied is None

    def test_not_upload_text_value_stash_if_uuid_not_on_value(self) -> None:
        """
        Do not upload stashed text values (standoff), if the resource has no value containing the UUID of the stashed
        text value in its text.
        """
        value_uuid = str(uuid4())
        property_name = "someprop"
        stash = Stash.make(
            standoff_stash=StandoffStash.make(
                [
                    StandoffStashItem(
                        "001", "sometype", value_uuid, property_name, FormattedTextValue("<p>some text</p>")
                    ),
                ]
            ),
            link_value_stash=None,
        )
        assert stash
        iri_resolver = IriResolver(
            {
                "001": "http://www.rdfh.ch/0001/001",
                "002": "http://www.rdfh.ch/0001/002",
            }
        )
        con: Connection = ConnectionMock(
            get_responses=[
                {
                    property_name: [
                        {
                            "@id": "http://www.rdfh.ch/0001/001/values/01",
                            "knora-api:textValueAsXml": "<p>not relevant</p>",
                        },
                    ],
                    "@context": {},
                },
            ],
            put_responses=[{}],
        )
        nonapplied = _upload_stash(
            stash=stash,
            iri_resolver=iri_resolver,
            con=con,
            verbose=False,
            project_client=ProjectClientStub(),
        )
        assert nonapplied == stash
