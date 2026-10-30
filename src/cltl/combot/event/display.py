from dataclasses import dataclass


@dataclass
class DisplayEvent:
    """A page for a person to look at, next to the conversation.

    `url` is what the browser loads, so it has to be one the *browser* can
    reach; `name` is what the person sees it called, on the tab and in the list
    of everything shown so far. Whether a url is shown at all is up to the
    consumer: cltl-chat-ui only takes http(s) urls on hosts it was told about.
    """
    url: str
    name: str

    def __post_init__(self):
        if not isinstance(self.url, str) or not self.url.strip():
            raise ValueError("a display needs a url: " + repr(self.url))
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("a display needs a name: " + repr(self.name))
