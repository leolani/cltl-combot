from typing import Optional

from cltl.combot.infra.event import Event


def event_payload_handler(handler):
    def wrapped(self, event):
        handler(self, event.payload)

    return wrapped


def extract_scenario_id(event: Event, on_missing: str = 'raise') -> Optional[str]:
    """
    Extract scenario_id from an event.

    First checks the event metadata for an explicit scenario_id.
    If not present, attempts to extract it from common payload structures:
    - Signal events: signal.time.container_id
    - Scenario events: scenario.id

    Parameters
    ----------
    event: Event
        Event to extract scenario_id from
    on_missing: str
        If 'raise' (default), raise an exception if an event is missing a scenario_id.
        Else returns None if the scenario.id is missing.

    Returns
    -------
    Optional[str]
        the scenario_id

    Returns None if scenario_id cannot be determined.
    """
    if hasattr(event.metadata, 'scenario_id') and event.metadata.scenario_id:
        return event.metadata.scenario_id

    if hasattr(event.payload, 'signal') and hasattr(event.payload.signal, 'time'):
        return event.payload.signal.time.container_id

    if hasattr(event.payload, 'scenario') and hasattr(event.payload.scenario, 'id'):
        return event.payload.scenario.id

    if on_missing == 'raise':
        raise ValueError('Missing scenario id in event: {}'.format(event))

    return None