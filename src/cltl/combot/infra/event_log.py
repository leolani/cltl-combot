import json
import logging
import os
import queue
from datetime import datetime
from multiprocessing import Process, Queue

logger = logging.getLogger(__name__)


class LogWriter:
    def __init__(self, log_dir: str, serializer):
        self._log_dir = log_dir
        self._serializer = serializer

        self._queue = Queue(maxsize=1024)
        self._writer_process = None

    def __enter__(self):
        self._writer_process = Process(target=self._process)
        self._writer_process.start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._writer_process is not None:
            self._queue.put(None)
            self._writer_process.join()
            self._writer_process = None

    def put(self, event):
        try:
            self._queue.put(event)
        except queue.Full:
            logger.exception("Event log overloaded: dropped event %s", event)

    def _process(self):
        log_file_path = self._get_event_log_path()
        with open(log_file_path, 'w') as log_file:
            logger.info("Writing event log at %s", log_file_path)

            log_file. write("[\n")

            event = ""
            while event is not None:
                try:
                    event = self._queue.get(block=True)
                except KeyboardInterrupt:
                    break
                log_file.write(json.dumps(event, default=self._serializer, indent=2) + ',\n')

            log_file.write("]\n")

        logger.info("Closed event log at %s", log_file_path)

    def _get_event_log_path(self):
        date_now = datetime.now()

        os.makedirs(self._log_dir, exist_ok=True)

        return f"{self._log_dir}/{date_now :%y_%m_%d-%H_%M_%S}.json"
