"""
The Pepper Framework Package consists out of the basic building blocks to make robot applications.

Abstract
========

The combot.application package contains specifications for:

- Applications: :class:`~cltl.combot.application.application.AbstractApplication`
- Components & Intentions: :class:`~cltl.combot.application.component.AbstractComponent` :class:`~cltl.combot.application.intention.AbstractIntention`

Backend
=======

The combot.backend package contains the backends implementing Sensors, Actuators & Backend:

- :class:`~cltl.combot.backend.naoqi.backend.NAOqiBackend` implements the backend for Pepper & Nao Robots
- :class:`~cltl.combot.backend.system.backend.SystemBackend` implements the backend for Windows/Mac/Linux systems.

Sensor
======

The combot.sensor package implements Face, Object and Speech Recognition:

- :class:`~cltl.combot.sensor.api.VAD` implements Voice Activity Detection on Microphone input
- :class:`~cltl.combot.sensor.api.ASR` implements Automated Speech Recognition
- :class:`~cltl.combot.sensor.api.ObjectDetector` implements Object Detection
- :class:`~cltl.combot.sensor.api.FaceDetector` implements Face Detection
- :class:`~cltl.combot.sensor.api.Location` gets the current geographical location (WIP)

Component
=========

Applications are made out of several instances of :class:`~cltl.combot.application.component.AbstractComponent`,
which expose various methods and events to applications. They are summarized below:

- :class:`~from cltl.combot.application.object_detection.ObjectDetectionComponent` exposes the :meth:`~cltl.combot.component.object_detection.ObjectDetectionComponent.on_object` event.
- :class:`~cltl.combot.component.face_detection.FaceRecognitionComponent` exposes the :meth:`~cltl.combot.component.face_detection.FaceRecognitionComponent.on_face`, :meth:`~cltl.combot.component.face_detection.FaceRecognitionComponentComponent.on_face_known` & :meth:`~cltl.combot.component.face_detection.FaceRecognitionComponent.on_face_new` events.
- :class:`~cltl.combot.component.text_to_speech.TextToSpeechComponent` exposes the :meth:`~cltl.combot.component.text_to_speech.TextToSpeechComponent.say` method.
- :class:`~cltl.combot.component.brain.BrainComponent` exposes :class:`pepper.brain.long_term_memory.LongTermMemory` to the application.

Some Components are more complex and require other components to work. They will raise a :class:`cltl.combot.application.component.ComponentDependencyError` if dependencies are not met.

- :class:`~cltl.combot.component.context.ContextComponent` exposes :class:`cltl.combot.context.Context` to the application and overrides the :meth:`~cltl.combot.component.context.ContextComponent.say` method to work with the :class:`~pepper.language.language.Chat` class. It also exposes the :meth:`~cltl.combot.component.context.ContextComponent.on_chat_turn`, :meth:`~cltl.combot.component.context.ContextComponent.on_chat_enter` & :meth:`~cltl.combot.component.context.ContextComponent.on_chat_exit` events.
- :class:`~cltl.combot.component.statistics.StatisticsComponent` displays realtime system statistics in the command line.
- :class:`~cltl.combot.component.scene.SceneComponent` creates a 3D scatterplot of the visible space.
- :class:`~cltl.combot.component.display.display.DisplayComponent` shows the live camera feedback and the 3D view of the current space, including the objects that are observed.

.. _pepper_tensorflow: https://github.com/cltl/pepper_tensorflow
"""