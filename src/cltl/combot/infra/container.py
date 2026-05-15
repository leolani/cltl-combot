from cltl.combot.infra.config.k8config import K8LocalConfigurationContainer
from cltl.combot.infra.event.kombu import KombuEventBusContainer
from cltl.combot.infra.resource.threaded import ThreadedResourceContainer


class InfraContainer(KombuEventBusContainer, K8LocalConfigurationContainer, ThreadedResourceContainer):
    """Base infrastructure container combining configuration, event bus, and resource management.

    Subclasses should override ``event_bus`` to select the concrete bus implementation
    (synchronous vs. Kombu) and ``event_bus_serializer`` to inject the appropriate
    serializer/deserializer pair for the event payload type.
    """

    def start(self):
        super().start()

    def stop(self):
        super().stop()
