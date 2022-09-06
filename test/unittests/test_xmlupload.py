"""Unit tests for xmlupload"""

import unittest
from lxml import etree

from knora.dsplib.models.helpers import BaseError
from knora.dsplib.utils.xml_upload import _convert_ark_v0_to_resource_iri, _remove_circular_references, _parse_xml_file
from knora.dsplib.models.xmlresource import XMLResource


class TestXMLUpload(unittest.TestCase):

    def test_convert_ark_v0_to_resource_iri(self) -> None:
        ark = "ark:/72163/080c-779b9990a0c3f-6e"
        iri = _convert_ark_v0_to_resource_iri(ark)
        self.assertEqual("http://rdfh.ch/080C/Ef9heHjPWDS7dMR_gGax2Q", iri)

        with self.assertRaises(BaseError) as err1:
            _convert_ark_v0_to_resource_iri("ark:/72163/080c-779b999-0a0c3f-6e")
        self.assertEqual(err1.exception.message, "while converting ARK 'ark:/72163/080c-779b999-0a0c3f-6e'. The ARK seems to be invalid")

        with self.assertRaises(BaseError) as err2:
            _convert_ark_v0_to_resource_iri("ark:/72163/080X-779b9990a0c3f-6e")
        self.assertEqual(err2.exception.message, "while converting ARK 'ark:/72163/080X-779b9990a0c3f-6e'. Invalid project shortcode '080X'")

        with self.assertRaises(BaseError) as err3:
            _convert_ark_v0_to_resource_iri("ark:/72163/080c1-779b9990a0c3f-6e")
        self.assertEqual(err3.exception.message, "while converting ARK 'ark:/72163/080c1-779b9990a0c3f-6e'. Invalid project shortcode '080C1'")

        with self.assertRaises(BaseError) as err3:
            _convert_ark_v0_to_resource_iri("ark:/72163/080c-779b99+90a0c3f-6e")
        self.assertEqual(err3.exception.message, "while converting ARK 'ark:/72163/080c-779b99+90a0c3f-6e'. Invalid Salsah ID '779b99+90a0c3f'")


    def test_remove_circular_references(self) -> None:
        # create a list of XMLResources from the test data file
        tree = _parse_xml_file('testdata/test-data-systematic.xml')
        resources = [XMLResource(x, 'testonto') for x in tree.getroot() if x.tag == "resource"]

        # get the purged resources and the stashes from the function to be tested
        resources, stashed_xml_texts_original, stashed_resptr_props_original = _remove_circular_references(resources, False)

        # make a list of all hashes from the stashed xml texts
        stashed_xml_texts_hashes = list()
        for res, propdict in stashed_xml_texts_original.items():
            for elem in propdict.values():
                for hash, xml in elem.items():
                    stashed_xml_texts_hashes.append(hash)

        # make a version of the stashes with the IDs from the XML file instead of the Python objects
        stashed_xml_texts = {res.id: {prop.name: [str(x) for x in d.values()] for prop, d in _dict.items()}
                             for res, _dict in stashed_xml_texts_original.items()}
        stashed_resptr_props = {res.id: {prop.name: l for prop, l in _dict.items()}
                                for res, _dict in stashed_resptr_props_original.items()}

        # hardcode the expected values
        stashed_xml_texts_expected = {
            'test_thing_1': {
                'testonto:hasRichtext': [
                    '\n                This is <em>bold and <strong>strong</strong></em> text! It contains links to all '
                    'resources:\n'
                    '                <a class="salsah-link" href="IRI:test_thing_0:IRI">test_thing_0</a>\n'
                    '                <a class="salsah-link" href="IRI:test_thing_1:IRI">test_thing_1</a>\n'
                    '                <a class="salsah-link" href="IRI:image_thing_0:IRI">image_thing_0</a>\n'
                    '                <a class="salsah-link" href="IRI:compound_thing_0:IRI">compound_thing_0</a>\n'
                    '                <a class="salsah-link" href="IRI:partof_thing_1:IRI">partof_thing_1</a>\n'
                    '                <a class="salsah-link" href="IRI:partof_thing_2:IRI">partof_thing_2</a>\n'
                    '                <a class="salsah-link" href="IRI:partof_thing_3:IRI">partof_thing_3</a>\n'
                    '                <a class="salsah-link" href="IRI:document_thing_1:IRI">document_thing_1</a>\n'
                    '                <a class="salsah-link" href="IRI:text_thing_1:IRI">text_thing_1</a>\n'
                    '                <a class="salsah-link" href="IRI:zip_thing_1:IRI">zip_thing_1</a>\n'
                    '                <a class="salsah-link" href="IRI:audio_thing_1:IRI">audio_thing_1</a>\n'
                    '                <a class="salsah-link" href="IRI:test_thing_2:IRI">test_thing_2</a>\n'
                    '            \n            '
                ]
            },
            'test_thing_2': {
                'testonto:hasRichtext': [
                     '\n                This is <em>bold and <strong>strong</strong></em> text! It contains links to all '
                     'resources:\n'
                     '                <a class="salsah-link" href="IRI:test_thing_0:IRI">test_thing_0</a>\n'
                     '                <a class="salsah-link" href="IRI:test_thing_1:IRI">test_thing_1</a>\n'
                     '                <a class="salsah-link" href="IRI:image_thing_0:IRI">image_thing_0</a>\n'
                     '                <a class="salsah-link" href="IRI:compound_thing_0:IRI">compound_thing_0</a>\n'
                     '                <a class="salsah-link" href="IRI:partof_thing_1:IRI">partof_thing_1</a>\n'
                     '                <a class="salsah-link" href="IRI:partof_thing_2:IRI">partof_thing_2</a>\n'
                     '                <a class="salsah-link" href="IRI:partof_thing_3:IRI">partof_thing_3</a>\n'
                     '                <a class="salsah-link" href="IRI:document_thing_1:IRI">document_thing_1</a>\n'
                     '                <a class="salsah-link" href="IRI:text_thing_1:IRI">text_thing_1</a>\n'
                     '                <a class="salsah-link" href="IRI:zip_thing_1:IRI">zip_thing_1</a>\n'
                     '                <a class="salsah-link" href="IRI:audio_thing_1:IRI">audio_thing_1</a>\n'
                     '                <a class="salsah-link" href="IRI:test_thing_2:IRI">test_thing_2</a>\n'
                     '            \n            '
                ]
            }
        }
        stashed_resptr_props_expected = {
            'test_thing_0': {'testonto:hasTestThing': ['test_thing_1']},
            'test_thing_1': {'testonto:hasResource': ['test_thing_2', 'link_obj_1']}
        }

        # check if the stashes are equal to the expected stashes
        self.assertDictEqual(stashed_resptr_props, stashed_resptr_props_expected)
        self.assertDictEqual(stashed_xml_texts, stashed_xml_texts_expected)

        # check if the stashed hashes can also be found at the correct position in the purged resources
        for res, propdict in stashed_xml_texts_original.items():
            for prop, hashdict in propdict.items():
                stashed_hashes = list(hashdict.keys())
                purged_res = resources[resources.index(res)]
                purged_prop = purged_res.properties[purged_res.properties.index(prop)]
                purged_hashes = [str(val.value) for val in purged_prop.values if str(val.value) in stashed_xml_texts_hashes]
                self.assertListEqual(stashed_hashes, purged_hashes)


if __name__ == '__main__':
    unittest.main()