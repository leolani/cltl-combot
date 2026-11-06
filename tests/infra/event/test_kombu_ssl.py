import ssl
import unittest
from unittest import mock

from cltl.combot.infra.event import kombu



class TestKombuSsl(unittest.TestCase):
    def _bus(self, **kombu_config):
        config_manager = mock.MagicMock()
        config = mock.MagicMock()
        values = dict(exchange="cltl.combot", compression="bzip2", tenant="", **kombu_config)
        config.get.side_effect = values.get
        config.__contains__.side_effect = values.__contains__
        config_manager.get_config.return_value = config

        with mock.patch.object(kombu, "Connection") as connection:
            kombu.KombuEventBus("cltl-json", config_manager)

        return connection

    def test_plain_amqp_has_no_ssl(self):
        connection = self._bus(server="amqp://u:p@rabbitmq:5672/")

        connection.assert_called_once_with("amqp://u:p@rabbitmq:5672/", ssl=False)

    def test_amqps_verifies_hostname(self):
        connection = self._bus(server="amqps://u:p@broker.example.org:5671/")

        connection.assert_called_once_with("amqps://u:p@broker.example.org:5671/",
                                           ssl={"server_hostname": None, "cert_reqs": ssl.CERT_REQUIRED})

    def test_amqps_with_custom_ca(self):
        connection = self._bus(server="amqps://u:p@broker.example.org:5671/", ssl_ca_certs="/ca.pem")

        connection.assert_called_once_with("amqps://u:p@broker.example.org:5671/",
                                           ssl={"server_hostname": None, "cert_reqs": ssl.CERT_REQUIRED,
                                                "ca_certs": "/ca.pem"})

    def test_empty_ca_means_system_store(self):
        connection = self._bus(server="amqps://u:p@broker.example.org:5671/", ssl_ca_certs="")

        self.assertNotIn("ca_certs", connection.call_args.kwargs["ssl"])
