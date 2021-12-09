import logging
import os

import cltl.combot.infra.config.local as local_config

logger = logging.getLogger(__name__)


K8_CONFIG_DIR = "/cltl_k8_config"
K8_CONFIG = "config/k8.config"


class K8LocalConfigurationContainer(local_config.LocalConfigurationContainer):
    @staticmethod
    def load_configuration(config_file=local_config.CONFIG, additional_config_files=local_config.ADDITIONAL_CONFIGS,
                           k8_configs=K8_CONFIG_DIR, k8_config_file=K8_CONFIG):
        configs = additional_config_files
        try:
            copy_k8_config(k8_configs, k8_config_file)
            configs += [k8_config_file]
        except OSError:
            logger.warning("Could not load kubernetes config map from %s to %s", k8_configs, k8_config_file)

        local_config.LocalConfigurationContainer.load_configuration(config_file, configs)


def copy_k8_config(k8_config_dir, k8_config_file):
    k8_configs = tuple(file for file in os.listdir(k8_config_dir) if not file.startswith("."))
    logger.debug("Found kubernetes config maps %s in %s", k8_configs, k8_config_dir)

    k8_sections = {section: _read_config(k8_config_dir, section)
                   for section in k8_configs}

    with open(k8_config_file, 'w') as k8_cfg:
        logger.info("Writing %s", k8_cfg)
        for section_name, section_values in k8_sections.items():
            k8_cfg.write(f"[{section_name}]\n")
            k8_cfg.write(section_values)
            k8_cfg.write("\n")


def _read_config(k8_configs, config_file):
    logger.info("Loading %s/%s", k8_configs, config_file)
    with open(os.path.join(k8_configs, config_file)) as cfg:
        return cfg.read()