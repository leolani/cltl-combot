import os
import unittest
import tempfile
import logging

import importlib.resources
from enum import Enum
from unittest.mock import patch

from cltl.combot.infra.di_container import DIContainer

from cltl.combot.infra.config.local import LocalConfigurationContainer


class TestEnum(Enum):
    VALUE = 1
    OTHER_VALUE = 2


class ConfigurationManagerCase(unittest.TestCase):
    def setUp(self):
        with importlib.resources.path(__package__, "test.config") as test_config:
            LocalConfigurationContainer.load_configuration(str(test_config), [])
        self.configuration_manager = LocalConfigurationContainer().config_manager

    def tearDown(self) -> None:
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
        default_config = self.configuration_manager.get_config("section")

        self.assertIsNotNone(default_config)
        self.assertTrue("name" in default_config)
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

    def test_contains(self):
        self.assertTrue(self.configuration_manager.has_config("section"))
        self.assertTrue("section" in self.configuration_manager)

        self.assertFalse(self.configuration_manager.has_config("not section"))
        self.assertFalse("not section" in self.configuration_manager)


class EnvInterpolationCase(unittest.TestCase):
    """Test cases for environment variable interpolation in config files."""

    def setUp(self):
        # Set up test environment variables
        self.original_env = os.environ.copy()
        os.environ['TEST_VAR'] = 'test_value'
        os.environ['TEST_HOST'] = 'localhost'
        os.environ['TEST_PORT'] = '8080'
        os.environ['TEST_PATH'] = '/var/app'

    def tearDown(self):
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
        DIContainer._reset()

    def _create_temp_config(self, content):
        """Helper to create a temporary config file."""
        fd, path = tempfile.mkstemp(suffix='.config', text=True)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)
            return path
        except:
            os.close(fd)
            raise

    def test_basic_env_var_substitution(self):
        """Test basic $VAR syntax substitution."""
        config_content = """
[test]
value: $TEST_VAR
host: $TEST_HOST
"""
        config_path = self._create_temp_config(config_content)
        try:
            LocalConfigurationContainer.load_configuration(config_path, [])
            config = LocalConfigurationContainer().config_manager.get_config("test")

            self.assertEqual("test_value", config.get("value"))
            self.assertEqual("localhost", config.get("host"))
        finally:
            os.unlink(config_path)

    def test_braced_env_var_substitution(self):
        """Test ${VAR} syntax substitution."""
        config_content = """
[test]
value: ${TEST_VAR}
host: ${TEST_HOST}
port: ${TEST_PORT}
"""
        config_path = self._create_temp_config(config_content)
        try:
            LocalConfigurationContainer.load_configuration(config_path, [])
            config = LocalConfigurationContainer().config_manager.get_config("test")

            self.assertEqual("test_value", config.get("value"))
            self.assertEqual("localhost", config.get("host"))
            self.assertEqual("8080", config.get("port"))
        finally:
            os.unlink(config_path)

    def test_mixed_env_var_substitution(self):
        """Test combination of environment variables and literal text."""
        config_content = """
[test]
url: http://${TEST_HOST}:${TEST_PORT}$TEST_PATH
mixed: prefix_${TEST_VAR}_suffix
ambiguous: prefix_$TEST_VAR
"""
        config_path = self._create_temp_config(config_content)
        try:
            LocalConfigurationContainer.load_configuration(config_path, [])
            config = LocalConfigurationContainer().config_manager.get_config("test")

            self.assertEqual("http://localhost:8080/var/app", config.get("url"))
            # Use ${VAR} syntax when variable is followed by valid identifier chars
            self.assertEqual("prefix_test_value_suffix", config.get("mixed"))
            # Without braces, underscore becomes part of the variable name
            self.assertEqual("prefix_test_value", config.get("ambiguous"))
        finally:
            os.unlink(config_path)

    def test_escaped_dollar_sign(self):
        """Test that $$ produces a literal $ sign."""
        config_content = """
[test]
currency: $$100
price: $$${TEST_PORT}
regex: ^\\d+$$
multiple: $$$$
"""
        config_path = self._create_temp_config(config_content)
        try:
            LocalConfigurationContainer.load_configuration(config_path, [])
            config = LocalConfigurationContainer().config_manager.get_config("test")

            self.assertEqual("$100", config.get("currency"))
            self.assertEqual("$8080", config.get("price"))
            self.assertEqual("^\\d+$", config.get("regex"))
            self.assertEqual("$$", config.get("multiple"))
        finally:
            os.unlink(config_path)

    @patch('cltl.combot.infra.config.local.logger')
    def test_missing_env_var_warning(self, mock_logger):
        """Test that missing environment variables trigger a warning."""
        config_content = """
[test]
missing: $NONEXISTENT_VAR
also_missing: ${ANOTHER_MISSING}
"""
        config_path = self._create_temp_config(config_content)
        try:
            LocalConfigurationContainer.load_configuration(config_path, [])
            config = LocalConfigurationContainer().config_manager.get_config("test")

            # Values should remain unexpanded
            self.assertEqual("$NONEXISTENT_VAR", config.get("missing"))
            self.assertEqual("${ANOTHER_MISSING}", config.get("also_missing"))

            # Should have logged warnings
            self.assertEqual(2, mock_logger.warning.call_count)
            warning_calls = [call[0][0] % call[0][1:] for call in mock_logger.warning.call_args_list]
            self.assertTrue(any("NONEXISTENT_VAR" in call for call in warning_calls))
            self.assertTrue(any("ANOTHER_MISSING" in call for call in warning_calls))
        finally:
            os.unlink(config_path)

    @patch('cltl.combot.infra.config.local.logger')
    def test_escaped_dollar_no_warning(self, mock_logger):
        """Test that escaped $$ doesn't trigger warnings."""
        config_content = """
[test]
currency: $$USD
price: $$100
"""
        config_path = self._create_temp_config(config_content)
        try:
            LocalConfigurationContainer.load_configuration(config_path, [])
            config = LocalConfigurationContainer().config_manager.get_config("test")

            self.assertEqual("$USD", config.get("currency"))
            self.assertEqual("$100", config.get("price"))

            # Should NOT have logged warnings for escaped $$
            mock_logger.warning.assert_not_called()
        finally:
            os.unlink(config_path)

    def test_environment_section_substitution(self):
        """Test that [environment] section values can reference env vars."""
        config_content = """
[test]
value: $ENV_FROM_SECTION

[environment]
ENV_FROM_SECTION: from_environment_section
ENV_WITH_SUBST: $TEST_VAR
"""
        config_path = self._create_temp_config(config_content)
        try:
            LocalConfigurationContainer.load_configuration(config_path, [])

            # Variables defined in [environment] should NOT be available during config parsing
            config = LocalConfigurationContainer().config_manager.get_config("test")
            # This should remain unexpanded because ENV_FROM_SECTION is set AFTER parsing
            self.assertEqual("$ENV_FROM_SECTION", config.get("value"))

            # But [environment] section values SHOULD be set as env vars after loading
            self.assertEqual("from_environment_section", os.environ.get('ENV_FROM_SECTION'))
            # And [environment] values CAN reference existing env vars
            self.assertEqual("test_value", os.environ.get('ENV_WITH_SUBST'))
        finally:
            os.unlink(config_path)

    def test_configparser_interpolation_combined(self):
        """Test that env vars work with ConfigParser's %(var)s interpolation."""
        config_content = """
[DEFAULT]
base_path: $TEST_PATH

[test]
full_path: %(base_path)s/subdir
combined: ${TEST_HOST}:%(base_path)s
"""
        config_path = self._create_temp_config(config_content)
        try:
            LocalConfigurationContainer.load_configuration(config_path, [])
            config = LocalConfigurationContainer().config_manager.get_config("test")

            # Environment vars expanded first, then ConfigParser interpolation
            self.assertEqual("/var/app/subdir", config.get("full_path"))
            self.assertEqual("localhost:/var/app", config.get("combined"))
        finally:
            os.unlink(config_path)

    def test_env_var_with_type_conversion(self):
        """Test that env vars work with type conversion methods."""
        os.environ['TEST_INT'] = '42'
        os.environ['TEST_FLOAT'] = '3.14'
        os.environ['TEST_BOOL'] = 'true'

        config_content = """
[test]
int_val: $TEST_INT
float_val: $TEST_FLOAT
bool_val: $TEST_BOOL
"""
        config_path = self._create_temp_config(config_content)
        try:
            LocalConfigurationContainer.load_configuration(config_path, [])
            config = LocalConfigurationContainer().config_manager.get_config("test")

            self.assertEqual(42, config.get_int("int_val"))
            self.assertEqual(3.14, config.get_float("float_val"))
            self.assertEqual(True, config.get_boolean("bool_val"))
        finally:
            os.unlink(config_path)

    def test_env_var_with_multi_values(self):
        """Test that env vars work with comma-separated multi-values."""
        os.environ['TEST_ITEMS'] = 'item1, item2, item3'

        config_content = """
[test]
items: $TEST_ITEMS
"""
        config_path = self._create_temp_config(config_content)
        try:
            LocalConfigurationContainer.load_configuration(config_path, [])
            config = LocalConfigurationContainer().config_manager.get_config("test")

            self.assertEqual(["item1", "item2", "item3"], config.get("items", multi=True))
        finally:
            os.unlink(config_path)

    def test_empty_env_var(self):
        """Test handling of empty environment variables."""
        os.environ['EMPTY_VAR'] = ''

        config_content = """
[test]
empty: $EMPTY_VAR
"""
        config_path = self._create_temp_config(config_content)
        try:
            LocalConfigurationContainer.load_configuration(config_path, [])
            config = LocalConfigurationContainer().config_manager.get_config("test")

            self.assertEqual("", config.get("empty"))
        finally:
            os.unlink(config_path)
