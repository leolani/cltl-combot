# CLTL Leolani Combot

CLTL Leolani Combot provides the framework for applications that implement human-robot interaction with conversation.

## About the Project

This is the successor of the [Leolani platform](https://github.com/leolani/pepper) with an improved modular architecture.

## Applications

Clone one of the application parents from this project space and follow the instructions there to run them:

* [Eliza app](https://github.com/leolani/eliza-parent)
* [Get to know you app](https://github.com/leolani/g2ky-parent)

## Components

Currently, the following components are implemented for the framework:

* [Application Repository](https://github.com/leolani/cltl-requirements)  
  Repository to share artifacts and external dependencies between components.
* [EMISSOR](https://github.com/leolani/emissor)  
  Representation of interaction data.
* [Backend](https://github.com/leolani/cltl-backend)  
  Hardware integration and signal generation.
* [Automatic Speech Recognition (ASR)](https://github.com/leolani/cltl-asr)  
  Transcription of audio signals to text.
* [Voice Activity Detection (VAD)](https://github.com/leolani/cltl-vad)  
  Detection of speech in audio signals.
* [Face Recognition](https://github.com/leolani/cltl-face-recognition)  
  Currently includes face detection, age-gender detection, face recognition
* [Chat UI](https://github.com/leolani/cltl-chat-ui)  
  Simple Chat client to display and interact with the conversation 
* [Eliza chat](https://github.com/leolani/cltl-eliza)  
  Eliza based chat.
* [Get To Know You (G2KY) chat](https://github.com/leolani/cltl-g2ky)  
  Establish name based on face recognition.

To create a new component follow the instructions in the [template component](https://github.com/leolani/cltl-template).

## Getting Started

### Running an application

Clone one of the above [applications](#Applications) and follow the instructions there to run them.

### Prerequisites

#### Python

Most of the repositories require at least Python 3.8.

One option to manage Python versions is to use
[pyenv](https://github.com/pyenv/pyenv). Note, however, that `pyenv` doesn't
work well together with anaconda. To detect if you are using anaconda, run
`which python`. If you use anaconda, you can use that to manage your Python
version.

#### make

To build the application, `make` is used.

On OS X it is recommeded to upgrade `make`. Since OS X doesn't use standard GNU
utils due their restrictive licence, default `make` on OS X is way outdated.

One option is to use homebrew:
    
    brew install make

and add the installed `gmake` command by adding

    PATH="$(brew --prefix)/opt/make/libexec/gnubin:$PATH"

to your `~/.zshrc`

#### Docker

To be added.

## Development

To work on the development of a specific [application](#applications), start from the parent repository
and follow the steps described below. The description uses the [Eliza app](https://github.com/leolani/eliza-parent)
as example.

### Check-out

To check out all code needed for the Eliza App, follow the instructions in the
[Eliza app](https://github.com/leolani/eliza-parent).

### Build and run the application

The application is structured into separate components which have their own *git* repositories
and can be run as separate Python applications. The parent repository of the application contains
all those component repositories as *git* submodules.

There is a central application ([cltl-eliza-app](https://github.com/leolani/cltl-eliza-app)) that configures and runs
all the necessary components it needs, either inside a Python application or as containerized services in a *Kubernetes*
cluster or using *docker compose*. To run the application, first all components need to be packaged and made available
to the application. For this purpose there are *makefiles* available in the components and the application parent that
automate this process. To build the application run

    make build

from the **parent repository**. This command will download external dependencies to
[cltl-requirements](https://github.com/leolani/cltl-requirements), setup virtual environments for all components, package
them and publish the packages to [cltl-requirements](https://github.com/leolani/cltl-requirements) to make them available
to the application and other components.

To run the application follow the instructions in the [Eliza parent](https://github.com/leolani/eliza-parent).

### Make changes to the code

Individual components in the parent repository are edited and committed separately, and, after a stable version is
reached, the state of the components is commited in the parent repository, for the workflow see
[Working with git submodules](HOWTO/gitsubmodules.md).   
Modularization allows developing components in isolation. The application and other components depend on a packaged
version of a component only, therefore changes will become available outside of the component only after rebuilding
the application, see above.

To use PyCharm for development see the instructions in [Workflow using PyCharm](HOWTO/pycharm.md).

To commit changes made to the application see the instructions in [Working with git submodules](HOWTO/gitsubmodules.md).

### Adding a new component

To add a new component to an application follow the instruction in the
[template component](https://github.com/leolani/cltl-template).

### Create a new application


### HOWTOs

* [Workflow using PyCharm](HOWTO/pycharm.md)
* [Working with git submodules](HOWTO/gitsubmodules.md)
* [Setup a new component](https://github.com/leolani/cltl-template.git)
* [Add a component to a Python app]()

## Content of this repository

This repo provides infrastructre and general code for the platform:

### Infrastructure

The `cltl.combot.infra` module contains library code for infrastructre used in
the application. 

#### Event bus

Components of the application can communicate via an event bus. The
`cltl.combot.infra.event` module provides the interface and different implementations
of the event bus.

The `cltl.combot.infra.topic_worker` module provides a convenience class to
implement the subscription to one or multiple topics in the event bus.

#### Configuration manager

Configuration is made available in the application via a configuration manager.
The `cltl.combot.infra.config` module provides the interface and different
implementations of the configuration manager. 

#### Resource manager

Access to resources in the application is made available via a resource manager.
This includes providing resources and waiting for resources to become available
as well as managing access to shared resources. The `cltl.combot.infra.resource`
module provides the interface and different implementations of the resource
manager. 

#### Time util

The `cltl.combot.infra.time_util` module provides time related utilities to
ease the usage of a consistent time format throughout the application.

#### Dependency injection

The `cltl.combot.infra.di_container` module provides a simple utility to use
dependency inject in the application. 

### Common libraries

To be added.

### Events based on EMISSOR

The `cltl.combot.event` module contains common event payloads.

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


<!-- LICENSE -->
## License

Distributed under the MIT License. See [`LICENSE`](https://github.com/leolani/cltl-combot/blob/main/LICENCE) for more information.



<!-- CONTACT -->
## Authors

* [Taewoon Kim](https://tae898.github.io/)
* [Thomas Baier](https://www.linkedin.com/in/thomas-baier-05519030/)
* [Selene Báez Santamaría](https://selbaez.github.io/)
* [Piek Vossen](https://github.com/piekvossen)
