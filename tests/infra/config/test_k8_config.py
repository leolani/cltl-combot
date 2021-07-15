import os
import tempfile
import unittest

import importlib.resources
from enum import Enum

from cltl.combot.infra.di_container import DIContainer

from cltl.combot.infra.config.k8config import K8LocalConfigurationContainer


class TestEnum(Enum):
    VALUE = 1
    OTHER_VALUE = 2


class ConfigurationManagerCase(unittest.TestCase):
    def setUp(self):
        _, self.k8_config_file = tempfile.mkstemp(prefix="test_k8_config_")

        with importlib.resources.path(__package__, "k8_configs") as k8_configs:
            K8LocalConfigurationContainer.load_configuration(config_file=None, additional_config_files=[],
                                                             k8_configs=str(k8_configs), k8_config_file=self.k8_config_file)
        self.configuration_manager = K8LocalConfigurationContainer().config_manager

    def tearDown(self) -> None:
        os.remove(self.k8_config_file)
        DIContainer._reset()

    def test_defaults(self):
        default_config = self.configuration_manager.get_config("DEFAULT")

        self.assertIsNotNone(default_config)
        self.assertEqual("test default", default_config.get("name"))
        self.assertEqual(2, default_config.get_int("int"))
        self.assertEqual(1.5, default_config.get_float("float"))
        self.assertEqual(True, default_config.get_boolean("bool"))
        self.assertEqual(True, default_config.get_boolean("bool_one"))
        self.assertEqual(True, default_config.get_boolean("bool_true"))
        self.assertEqual(True, default_config.get_boolean("bool_yes"))
        self.assertEqual(True, default_config.get_boolean("bool_on"))
        self.assertEqual(False, default_config.get_boolean("bool_zero"))
        self.assertEqual(False, default_config.get_boolean("bool_false"))
        self.assertEqual(False, default_config.get_boolean("bool_no"))
        self.assertEqual(False, default_config.get_boolean("bool_off"))
        self.assertEqual(TestEnum.VALUE, default_config.get_enum("enum", TestEnum))

    def test_section(self):
        default_config = self.configuration_manager.get_config("cltl.test.section")

        self.assertIsNotNone(default_config)
        self.assertEqual("test section", default_config.get("name"))
        self.assertEqual(["val_1", "val_2"], default_config.get("values", multi=True))
        self.assertEqual(3, default_config.get_int("int"))
        self.assertEqual(2.5, default_config.get_float("float"))
        self.assertEqual(True, default_config.get_boolean("bool"))
        self.assertEqual(True, default_config.get_boolean("bool_one"))
        self.assertEqual(True, default_config.get_boolean("bool_true"))
        self.assertEqual(True, default_config.get_boolean("bool_yes"))
        self.assertEqual(True, default_config.get_boolean("bool_on"))
        self.assertEqual(False, default_config.get_boolean("bool_zero"))
        self.assertEqual(False, default_config.get_boolean("bool_false"))
        self.assertEqual(False, default_config.get_boolean("bool_no"))
        self.assertEqual(False, default_config.get_boolean("bool_off"))
        self.assertEqual(TestEnum.VALUE, default_config.get_enum("enum", TestEnum))
        self.assertEqual([TestEnum.VALUE, TestEnum.OTHER_VALUE], default_config.get_enum("enums", TestEnum, multi=True))
        self.assertEqual("default/test section/True", default_config.get("interpolated"))

    def test_environment(self):
        self.assertEqual("test environment variable", os.environ['UNIT_TEST_VAR'])
