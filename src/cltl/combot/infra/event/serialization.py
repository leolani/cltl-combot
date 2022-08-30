import base64
from json import JSONEncoder

import numpy as np


class NumpyJSONEncoder(JSONEncoder):
    def __init__(self, *, delegate: JSONEncoder = None, **kwargs):
        super().__init__(**kwargs)
        self._delegate = delegate

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return {
                "__type": "np.ndarray",
                "data": base64.b64encode(obj.tobytes()).decode('ascii'),
                "shape": obj.shape,
                "dtype": str(obj.dtype)
            }

        return self._delegate.default(obj) if self._delegate else super().default(obj)


def numpy_object_hook(obj):
    if not isinstance(obj, dict) or "__type" not in obj or obj["__type"] != "np.ndarray":
        return obj

    data_string = obj["data"]
    shape = obj["shape"]
    dtype = obj["dtype"]

    return np.frombuffer(base64.b64decode(data_string), dtype=dtype).reshape(shape)
