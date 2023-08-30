################################################################################
#  Python Package to Support 42crunch System Deployment
#
#    Author: Sam Li <yang.li@owasp.org>
#
#       2022 - 2023
################################################################################

import unittest, os
from crunch_support.util import *

class TestUtil(unittest.TestCase):

    def test_run_commnand(self):
        code,out,err = run_command("echo 'hello world'")
        self.assertEqual("hello world\n",out)
        self.assertEqual(None,code)
        self.assertEqual('',err)

    def test_is_file(self):
        test_file = """\
        This is a test file
        """
        with open(".test.txt","w") as f:
            f.write(test_file)
        try:
            self.assertEqual(True,is_file(".test.txt"))
        finally:
            os.unlink(".test.txt")

    def test_is_directory(self):
        os.mkdir("foo") # create foo sub-directory
        try:
            self.assertEqual(True,is_directory("foo"))
        finally:
            os.rmdir("foo")

    def test_strip_non_alpha_num(self):
        random_text = "Letter$$ wooded direct two men! indeed income sister. Impression up admiration he by partiality is. Instantly immediate his saw one day perceived. Old blushes respect but offices hearted minutes effects. Written parties winding oh as in without on started. Residence gentleman yet preserved few convinced. Coming regret simple longer little am sister on. Do danger in to adieus ladies houses oh eldest. Gone pure late gay ham. They sigh were not find are rent"
        encoded_text = strip_non_alpha_num(random_text)
        self.assertEqual("LetterwoodeddirecttwomenindeedincomesisterImpressionupadmirationhebypartialityisInstantlyimmediatehissawonedayperceivedOldblushesrespectbutofficesheartedminuteseffectsWrittenpartieswindingohasinwithoutonstartedResidencegentlemanyetpreservedfewconvincedComingregretsimplelongerlittleamsisteronDodangerintoadieusladieshousesoheldestGonepurelategayhamTheysighwerenotfindarerent",encoded_text)

    def test_get_swagger_dict(self):
        json_file = "tests/test_get_swagger_dict.json"
        yaml_file = "tests/test_get_swagger_dict.yaml"
        dict_1 = get_swagger_dict(yaml_file,True)
        dict_2 = get_swagger_dict(json_file, False)
        self.assertEqual(dict_1, dict_2)
