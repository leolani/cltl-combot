from typing import Optional


def event_payload_handler(handler):
    def wrapped(self, event):
        handler(self, event.payload)

    return wrapped


def extract_scenario_id(event) -> Optional[str]:
    """
    Extract scenario_id from an event.

    First checks the event metadata for an explicit scenario_id.
    If not present, attempts to extract it from common payload structures:
    - Signal events: signal.time.container_id
    - Scenario events: scenario.id

    Returns None if scenario_id cannot be determined.
    """
    if event.metadata.scenario_id:
        return event.metadata.scenario_id

    if hasattr(event.payload, 'signal') and hasattr(event.payload.signal, 'time'):
        return event.payload.signal.time.container_id

    if hasattr(event.payload, 'scenario') and hasattr(event.payload.scenario, 'id'):
        return event.payload.scenario.id

    return None