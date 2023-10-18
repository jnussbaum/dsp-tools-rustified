from __future__ import annotations

from dataclasses import dataclass
from itertools import groupby

from dsp_tools.models.value import KnoraStandoffXml
from dsp_tools.models.xmlresource import XMLResource


@dataclass(frozen=True)
class StandoffStashItem:
    """Holds information about a single stashed XML text value."""

    uuid: str
    prop_name: str
    value: KnoraStandoffXml
    # Permissions missing still


@dataclass(frozen=True)
class StandoffStash:
    """Holds information about a number of stashed XML text values, organized by resource instance."""

    res_2_stash_items: dict[str, list[StandoffStashItem]]
    res_2_xmlres: dict[str, XMLResource]

    @staticmethod
    def make(tups: list[tuple[XMLResource, StandoffStashItem]]) -> StandoffStash | None:
        """
        Factory method for StandoffStash.

        Args:
            tups: A list of tuples of XMLResource and StandoffStashItem.

        Returns:
            StandoffStash | None: A StandoffStash object or None, if an empty list was passed.
        """
        if not tups:
            return None
        res_2_stash_items = {}
        res_2_xmlres = {}
        for xmlres, stash_item in tups:
            if xmlres.id not in res_2_stash_items:
                res_2_stash_items[xmlres.id] = [stash_item]
                res_2_xmlres[xmlres.id] = xmlres
            else:
                res_2_stash_items[xmlres.id].append(stash_item)
        return StandoffStash(res_2_stash_items, res_2_xmlres)


@dataclass(frozen=True)
class LinkValueStashItem:
    """Holds information about a single stashed link value."""

    res_id: str
    res_type: str
    prop_name: str
    target_id: str


@dataclass(frozen=True)
class LinkValueStash:
    """Holds information about a number of stashed link values (resptr-props), organized by resource instance."""

    res_2_stash_items: dict[str, list[LinkValueStashItem]]

    @staticmethod
    def make(items: list[LinkValueStashItem]) -> LinkValueStash | None:
        """
        Factory method for LinkValueStash.

        Args:
            items: A list of LinkValueStashItem.

        Returns:
            LinkValueStash | None: A LinkValueStash object or None, if an empty list was passed.
        """
        if not items:
            return None
        grouped_objects = {k: list(vals) for k, vals in groupby(items, key=lambda x: x.res_id)}
        return LinkValueStash(grouped_objects)


@dataclass(frozen=True)
class Stash:
    """Holds a standoff stash and a linkvalue stash"""

    standoff_stash: StandoffStash | None
    link_value_stash: LinkValueStash | None

    @staticmethod
    def make(standoff_stash: StandoffStash | None, link_value_stash: LinkValueStash | None) -> Stash | None:
        """
        Factory method for Stash.

        Args:
            standoff_stash: A StandoffStash object or None.
            link_value_stash: A LinkValueStash object or None.

        Returns:
            Stash: A Stash object, or None if both iunputs are None.
        """
        if standoff_stash or link_value_stash:
            return Stash(standoff_stash, link_value_stash)
        return None