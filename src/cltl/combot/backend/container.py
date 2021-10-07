from cltl.combot.backend.api.backend import AbstractBackend
from cltl.combot.infra.di_container import DIContainer


class BackendContainer(DIContainer):
    @property
    def backend(self):
        # type: () -> AbstractBackend
        """
        Returns
        -------
        backend: AbstractBackend :class:`~cltl.combot.backend.api.AbstractBackend`
        """
        raise ValueError("No backend configured")
