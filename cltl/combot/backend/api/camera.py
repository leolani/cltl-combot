import json
import logging
import os
from collections import deque
from time import time, strftime, localtime

import enum as enum
import numpy as np
from PIL import Image
from typing import Tuple, List, Optional

from cltl.combot.infra.event.api import Event, EventBus
from cltl.combot.infra.resource.api import ResourceManager
from cltl.combot.infra.util import Mailbox, Scheduler, Bounds, spherical2cartesian

logger = logging.getLogger(__name__)


TOPIC = "cltl.combot.backend.api.camera.topic"


class CameraResolution(enum.Enum):
    NATIVE = -1, -1
    QQQQVGA = 30, 40
    QQQVGA = 60, 80
    QQVGA = 120, 160
    QVGA = 240, 320
    VGA = 480, 640
    VGA4 = 960, 1280


class Image(object):
    """
    Abstract Image Container

    Parameters
    ----------
    image: np.ndarray
        RGB Image (height, width, 3) as Numpy Array
    bounds: Bounds
        Image Bounds (View Space) in Spherical Coordinates (Phi, Theta)
    depth: np.ndarray
        Depth Image (height, width) as Numpy Array
    """
    def __init__(self, image, bounds, depth=None, image_time=None):
        # type: (np.ndarray, Bounds, Optional[np.ndarray]) -> None

        self._image = image
        self._bounds = bounds
        self._depth = np.ones((100, 100), np.float32) if depth is None else depth

        self._time = image_time if image_time else time()

    @property
    def hash(self):
        return "{}_{}".format(strftime("%Y%m%d_%H%M%S", localtime(self.time)), str(self.time % 1)[2:4])

    @property
    def image(self):
        # type: () -> np.ndarray
        """
        RGB Image (height, width, 3) as Numpy Array

        Returns
        -------
        image: np.ndarray
            RGB Image (height, width, 3) as Numpy Array
        """
        return self._image

    @property
    def depth(self):
        # type: () -> Optional[np.ndarray]
        """
        Depth Image (height, width) as Numpy Array

        Returns
        -------
        depth: np.ndarray
            Depth Image (height, width) as Numpy Array
        """
        return self._depth

    @property
    def bounds(self):
        # type: () -> Bounds
        """
        Image Bounds (View Space) in Spherical Coordinates (Phi, Theta)

        Returns
        -------
        bounds: Bounds
            Image Bounds (View Space) in Spherical Coordinates (Phi, Theta)
        """
        return self._bounds

    def get_image(self, bounds):
        # type: (Bounds) -> np.ndarray
        """
        Get pixels from Image at Bounds in Image Space

        Parameters
        ----------
        bounds: Bounds
            Image Bounds (Image) in Image Space (y, x)

        Returns
        -------
        pixels: np.ndarray
            Requested pixels within Bounds
        """

        x0 = int(bounds.x0 * self._image.shape[1])
        x1 = int(bounds.x1 * self._image.shape[1])
        y0 = int(bounds.y0 * self._image.shape[0])
        y1 = int(bounds.y1 * self._image.shape[0])

        return self._image[y0:y1, x0:x1]

    def get_depth(self, bounds):
        # type: (Bounds) -> Optional[np.ndarray]
        """
        Get depth from Image at Bounds in Image Space

        Parameters
        ----------
        bounds: Bounds
            Image Bounds (Image) in Image Space (y, x)

        Returns
        -------
        depth: np.ndarray
            Requested depth within Bounds
        """

        if self._depth is None:
            return None

        x0 = int(bounds.x0 * self._depth.shape[1])
        x1 = int(bounds.x1 * self._depth.shape[1])
        y0 = int(bounds.y0 * self._depth.shape[0])
        y1 = int(bounds.y1 * self._depth.shape[0])

        return self._depth[y0:y1, x0:x1]

    def get_direction(self, coordinates):
        # type: (Tuple[float, float]) -> Tuple[float, float]
        """
        Convert 2D Image Coordinates [x, y] to 2D position in Spherical Coordinates [phi, theta]

        Parameters
        ----------
        coordinates: Tuple[float, float]

        Returns
        -------
        direction: Tuple[float, float]
        """
        return (self.bounds.x0 + coordinates[0] * self.bounds.width,
                self.bounds.y0 + coordinates[1] * self.bounds.height)

    @property
    def time(self):
        # type: () -> float
        """
        Get time image was captured and received by the application.

        Returns
        -------
        time: float
        """
        return self._time

    def frustum(self, depth_min, depth_max):
        # type: (float, float) -> List[float]
        """
        Calculate `Frustum <https://en.wikipedia.org/wiki/Viewing_frustum>`_ of the camera at image time (visualisation)

        Parameters
        ----------
        depth_min: float
            Near Viewing Plane
        depth_max: float
            Far Viewing Place

        Returns
        -------
        frustum: List[float]
        """
        return [

            # Near Viewing Plane
            spherical2cartesian(self._bounds.x0, self._bounds.y0, depth_min),
            spherical2cartesian(self._bounds.x0, self._bounds.y1, depth_min),
            spherical2cartesian(self._bounds.x1, self._bounds.y1, depth_min),
            spherical2cartesian(self._bounds.x1, self._bounds.y0, depth_min),

            # Far Viewing Plane
            spherical2cartesian(self._bounds.x0, self._bounds.y0, depth_max),
            spherical2cartesian(self._bounds.x0, self._bounds.y1, depth_max),
            spherical2cartesian(self._bounds.x1, self._bounds.y1, depth_max),
            spherical2cartesian(self._bounds.x1, self._bounds.y0, depth_max),
        ]

    def to_file(self, root):

        if not os.path.exists(os.path.dirname(root)):
            os.makedirs(os.path.dirname(root))

        # Save RGB Image
        Image.fromarray(self.image).save(os.path.join(root, "{}_rgb.png".format(self.hash)))

        # Save Depth Image
        np.save(os.path.join(root, "{}_depth.npy".format(self.hash)), self.depth)

        # Save Metadata
        with open(os.path.join(root, "{}_meta.json".format(self.hash)), 'w') as json_file:
            json.dump({
                "time": self.time,
                "bounds": self.bounds.dict()
            },json_file)

    def __repr__(self):
        return "{}{}".format(self.__class__.__name__, self.image.shape)


class AbstractCamera(object):
    def __init__(self, resolution, rate, event_bus, resource_manager):
        # type: (CameraResolution, int, EventBus, ResourceManager) -> None
        """
        Abstract Camera

        Parameters
        ----------
        resolution: CameraResolution
            :class:`~pepper.config.CameraResolution`
        rate: int
            Camera Frames per Second
        event_bus: EventBus
            Event bus of the application
        """
        self._log = logger.getChild(self.__class__.__name__)

        # Extract Image Dimensions from CameraResolution
        self._resolution = resolution
        self._width = self._resolution.value[1]
        self._height = self._resolution.value[0]
        self._event_bus = event_bus
        self._resource_manager = resource_manager

        self._rate = rate
        # Variables to do some performance statistics
        self._true_rate = rate
        self._dt_buffer = deque([], maxlen=10)
        self._t0 = time()

        # Create Mailbox and Image Processor:
        #   Each time an image is captured it is put in the mailbox, overriding whatever there might currently be.
        #   In a separate thread, the _processor worker takes an image and publishes it as event.
        #   This way the processing of images does not block the acquisition of new images,
        #   while at the same new images don't build up a queue, but are discarded when the _processor is too busy.
        self._mailbox = Mailbox()
        self._processor_scheduler = None

        # Default behaviour is to not run by default. Calling AbstractApplication.run() will activate the camera
        self._running = False

    @property
    def true_rate(self):
        # type: () -> float
        """
        Actual Image Rate (Frames per Second)

        Image rate after accounting for latency & performance realities

        Returns
        -------
        true_rate: float
            Actual Image Rate (Frames per Second)
        """
        return self._true_rate

    @property
    def running(self):
        # type: () -> bool
        """
        Returns whether Camera is Running

        Returns
        -------
        running: bool
        """
        return self._processor_scheduler.running if self._processor_scheduler else False

    def on_image(self, image):
        # type: (Image) -> None
        """
        On Image Event, Called for every Image captured by Camera

        Custom Camera Backends should call this function for every frame acquired by the Camera

        Parameters
        ----------
        image: Image
        """
        self._mailbox.put(image)

    def start(self):
        """Start Streaming Images from Camera"""
        if self._running:
            raise RuntimeError()

        self._processor_scheduler = Scheduler(self._processor, name="CameraThread")
        self._processor_scheduler.start()
        self._running = True
        self._resource_manager.provide_resource(TOPIC)

    def stop(self):
        """Stop Streaming Images from Camera"""
        self._running = False
        self._resource_manager.retract_resource(TOPIC)
        self._processor_scheduler.stop()

    def _processor(self):
        """
        Image Processor

        Calls each callback for each image, threaded, for higher image throughput and less image latency
        """

        # Get latest image from Mailbox
        image = self._mailbox.get()

        self._event_bus.publish(TOPIC, Event(image, None))

        # Update Statistics
        self._update_dt()

    def _update_dt(self):
        t1 = time()
        self._dt_buffer.append((t1 - self._t0))
        self._t0 = t1
        self._true_rate = 1 / np.mean(self._dt_buffer)
