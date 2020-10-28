"""
The Pepper Framework Package consists out of the basic building blocks to make robot applications.

Abstract
========

The framework.application package contains specifications for:

- Applications: :class:`~leolani.framework.application.application.AbstractApplication`
- Components & Intentions: :class:`~leolani.framework.application.component.AbstractComponent` :class:`~leolani.framework.application.intention.AbstractIntention`

Backend
=======

The framework.backend package contains the backends implementing Sensors, Actuators & Backend:

- :class:`~leolani.framework.backend.naoqi.backend.NAOqiBackend` implements the backend for Pepper & Nao Robots
- :class:`~leolani.framework.backend.system.backend.SystemBackend` implements the backend for Windows/Mac/Linux systems.

Sensor
======

The framework.sensor package implements Face, Object and Speech Recognition:

- :class:`~leolani.framework.sensor.api.VAD` implements Voice Activity Detection on Microphone input
- :class:`~leolani.framework.sensor.api.ASR` implements Automated Speech Recognition
- :class:`~leolani.framework.sensor.api.ObjectDetector` implements Object Detection
- :class:`~leolani.framework.sensor.api.FaceDetector` implements Face Detection
- :class:`~leolani.framework.sensor.api.Location` gets the current geographical location (WIP)

Component
=========

Applications are made out of several instances of :class:`~leolani.framework.application.component.AbstractComponent`,
which expose various methods and events to applications. They are summarized below:

- :class:`~from leolani.framework.application.object_detection.ObjectDetectionComponent` exposes the :meth:`~leolani.framework.component.object_detection.ObjectDetectionComponent.on_object` event.
- :class:`~leolani.framework.component.face_detection.FaceRecognitionComponent` exposes the :meth:`~leolani.framework.component.face_detection.FaceRecognitionComponent.on_face`, :meth:`~leolani.framework.component.face_detection.FaceRecognitionComponentComponent.on_face_known` & :meth:`~leolani.framework.component.face_detection.FaceRecognitionComponent.on_face_new` events.
- :class:`~leolani.framework.component.text_to_speech.TextToSpeechComponent` exposes the :meth:`~leolani.framework.component.text_to_speech.TextToSpeechComponent.say` method.
- :class:`~leolani.framework.component.brain.BrainComponent` exposes :class:`pepper.brain.long_term_memory.LongTermMemory` to the application.

Some Components are more complex and require other components to work. They will raise a :class:`leolani.framework.application.component.ComponentDependencyError` if dependencies are not met.

- :class:`~leolani.framework.component.context.ContextComponent` exposes :class:`leolani.framework.context.Context` to the application and overrides the :meth:`~leolani.framework.component.context.ContextComponent.say` method to work with the :class:`~pepper.language.language.Chat` class. It also exposes the :meth:`~leolani.framework.component.context.ContextComponent.on_chat_turn`, :meth:`~leolani.framework.component.context.ContextComponent.on_chat_enter` & :meth:`~leolani.framework.component.context.ContextComponent.on_chat_exit` events.
- :class:`~leolani.framework.component.statistics.StatisticsComponent` displays realtime system statistics in the command line.
- :class:`~leolani.framework.component.scene.SceneComponent` creates a 3D scatterplot of the visible space.
- :class:`~leolani.framework.component.display.display.DisplayComponent` shows the live camera feedback and the 3D view of the current space, including the objects that are observed.

.. _pepper_tensorflow: https://github.com/cltl/pepper_tensorflow
"""