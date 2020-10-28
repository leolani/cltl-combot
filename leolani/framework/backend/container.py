from leolani.framework.backend.api.backend import AbstractBackend
from leolani.framework.infra.di_container import DIContainer

class BackendContainer(DIContainer):
    @property
    def backend(self):
        # type: () -> AbstractBackend
        """
        Returns
        -------
        backend: AbstractBackend :class:`~leolani.framework.backend.api.AbstractBackend`
        """
        raise ValueError("No backend configured")