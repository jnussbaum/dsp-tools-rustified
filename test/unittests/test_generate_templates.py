import shutil
import unittest
from pathlib import Path

from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.generate_templates import generate_template_repo


class TestGenerateTemplates(unittest.TestCase):
    def test_generate_template_repo(self) -> None:
        success = generate_template_repo()
        self.assertTrue(success)

        with self.assertRaisesRegex(UserError, "already exists in your current working directory"):
            generate_template_repo()
        
        self.assertTrue(Path("0100-template-repo/template.json").exists())
        self.assertTrue(Path("0100-template-repo/template.xml").exists())

        shutil.rmtree("0100-template-repo")