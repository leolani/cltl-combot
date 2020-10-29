# Modularization

An individual service will be containerized, effectively achieving process-level isolation. This is regarded a good practice as of writing this post, 2020-10-27\. Each service will have its own repo so that they can be tested individually.

## NLP, NLU, and the brain

_This will have multiple repos with Dockerfiles._

This is the most important and novel part but unfortunately I don’t have much experience with it. I’ll closely follow what the CLTL people have done: [https://github.com/cltl-leolani/pepper](https://github.com/cltl-leolani/pepper)

> TODO:
> 
> Understand the repo better https://github.com/cltl-leolani/pepper

## Object detector

_This will have a separate repo and a Dockerfile._

There is an existing one: [https://github.com/cltl-leolani/pepper_tensorflow](https://github.com/cltl-leolani/pepper_tensorflow). It’s a good start but we can do better by using a SOTA object detector (e.g. YOLOv4) and enabling GPU. Also porting tensorflow to pytorch would be nice.

> TODO:
> 
> Create a repo. An off-the-shelf one (e.g. YOLO) will do. Make a GPU option also available. Pytorch is preferred. Otherwise tensorflow is also okay. Create a Dockerfile. Obviously this will be a server. Should this run as a flask API? Is this fast enough btw?

## Face detector

_This will have a separate repo and a Dockerfile._

Probably most of the off-the-shelf face detectors will work fine. Even HoG + SVM models will work just right. But let’s try to use a DNN one.

> TODO:
> 
> Create a repo. An off-the-shelf one will do (even a lightweight one will work just okay). Make a GPU option also available. Pytorch is preferred. Otherwise tensorflow is also okay. Create a Dockerfile. Obviously this will be a server. Should this run as a flask API? Is this fast enough btw?

## Face recognizer

_This will have a separate repo and a Dockerfile._

Use something like [arcface](https://arxiv.org/abs/1801.07698), which can give us a pretty high dimensional vector.

> TODO:
> 
> Create a repo. An off-the-shelf one (e.g. arcface) will do. Make a GPU option also available. Pytorch is preferred. Otherwise tensorflow is also okay. Create a Dockerfile. Obviously this will be a server. Should this run as a flask API? Is this fast enough btw?

## Face landmark detector

In the end the landmarks can be used to generate a face. This will even allow us to generate an interactive face using only one face template! (i.e. deepfake). Imagine you’ll be talking to Einstein or Mona Lisa. That’s just cool. Use something that can give you a lot of landmarks (e.g. dlib 68 landmarks).

> TODO:
> 
> Create a repo. An off-the-shelf one (dlib) will do. Make a GPU option also available. Pytorch is preferred. Otherwise tensorflow is also okay. Create a Dockerfile. Obviously this will be a server. Should this run as a flask API? Is this fast enough btw?

## Speech to text (STT)

_This will have a separate repo and a Dockerfile._

> TODO:
> 
> Create a repo. An off-the-shelf one will do. Make a GPU option also available. Pytorch is preferred. Otherwise tensorflow is also okay. Create a Dockerfile. Obviously this will be a server. Should this run as a flask API? Is this fast enough btw?

## Text to speech (TTS)

_This will have a separate repo and a Dockerfile._

> TODO:
> 
> Create a repo. An off-the-shelf one will do. Make a GPU option also available. Pytorch is preferred. Otherwise tensorflow is also okay. Create a Dockerfile. Obviously this will be a server. Should this run as a flask API? Is this fast enough btw?

## Text to face

_This will have a separate repo and a Dockerfile._

I actually have no idea how this will work. What I have in mind is that when text is generated and as Leolani uses TTS to vocalize the text, also corresponding realistic face expressions should be generated together. This is one of the reasons why I want to push the virtual Leolani. Existing physical robots can’t do this.

> TODO:
> 
> _Think about what you can do._

## Emotion/sentiment classification

_This will have a separate repo and a Dockerfile._

Refer to https://github.com/declare-lab/conv-emotion

> TODO:
> 
> Create a repo. An off-the-shelf one will do. Make a GPU option also available. Pytorch is preferred. Otherwise tensorflow is also okay. Create a Dockerfile. Obviously this will be a server. Should this run as a flask API? Is this fast enough btw?

## Age/Gender classification

_This will have a separate repo and a Dockerfile._

Refer to https://github.com/GilLevi/AgeGenderDeepLearning

> TODO:
> 
> Create a repo. An off-the-shelf one will do. Make a GPU option also available. Pytorch is preferred. Otherwise tensorflow is also okay. Create a Dockerfile. Obviously this will be a server. Should this run as a flask API? Is this fast enough btw?

## GraphDB

Is this part of the brain?

> TODO:
> 
> Understand better

# Interface

The repo [https://github.com/cltl-leolani/virtual-leolani](https://github.com/cltl-leolani/virtual-leolani) is where the interface between the user and Leolani happens. Ideally when you clone it and start the application, all of the above repos will be cloned together. This repo has `docker-compose.yml` which will start all the other necessary docker containers.

> TODO:
> 
> Create a dummy interface layout.
> 
> Make two graphical windows, one for what Leolani sees and the other for what you see as a user.

Webcam and microphone recording, speaker output, and Leolani face rendering will be handled here. Should all of them run on separate threads so that they can be done somewhat simultaneously?

> TODO:
> 
> Get Webcam, microphone, and speaker to work in python3\. Find a way to make them run in separate threads so that we can process them somewhat simultaneously.



# Actual repos created

cltl-template
cltl-docker
cltl-combot (WIP)
cltl-vad
cltl-stt

cltl-objectdetection (WIP)
cltl-facedetection
cltl-facerecognition
cltl-facelandmark
cltl-agedetection
cltl-genderdetection
cltl-facegeneration
cltl-emotionrecognition     
cltl-sentimentrecognition   
  
cltl-knowledgeextraction
cltl-knowledgerepresentation (WIP)
cltl-commonsense
cltl-tts
