# CLTL Leolani Combot

CLTL Leolani Combot provides the framework for applications that implement human-robot interaction with conversation.

## About the Project

This is the successor of the [Leolani platform](https://github.com/leolani/pepper) with an improved modular
architecture.

## Applications

Clone one of the application parents from this project space and follow the instructions there to run them:

* [Eliza app](https://github.com/leolani/eliza-parent)
* [Get to know you app](https://github.com/leolani/g2ky-parent)
* [Leolani-mmai](https://github.com/leolani/leolani-mmai-parent)

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
* [About-agent](https://github.com/leolani/cltl-about-agent)
  Answer questions about the agent itself.
* [Knowledge extraction](https://github.com/leolani/cltl-knowledgeextraction)
  Extracts factoid triples and perspectives from statements and gives back responses or it extracts SPARQL queries from
  questions and generates answers.
* [Knowledge linking](https://github.com/leolani/cltl-knowledgelinking)
  Resolves IRIs for mentions and perceptions of things and people such that triples are augmented with IRIs.
* [Knowledge representation](https://github.com/leolani/cltl-knowledgerepresentation)
  The models and functions to support the episodic Knowledge Graph.
* [Language generation](https://github.com/leolani/cltl-languagegeneration)
  Generates texts from triples.
* [Mention detection](https://github.com/leolani/cltl-mention-detection)
  Detects mentions of entities and visual objects in text.
* [Object recognition](https://github.com/leolani/cltl-object-recognition)
  Detects people and objects in images.
* [Question processor](https://github.com/leolani/cltl-questionprocessor)
  Answers questions about the world through the Internet.
* [Visual responder](https://github.com/leolani/cltl-visualresponder)
  Answers questions to the visual context.

To create a new component follow the instructions in the [template component](https://github.com/leolani/cltl-template).

## Getting Started

### Running an application

Clone one of the above [applications](#Applications) and follow the instructions there to run them.

### Prerequisites

#### Homebrew

[Homebrew](https://brew.sh/) is a useful package manager for Mac OS X, to install it follow the
instructions on their homepage.

#### Python

Most of the repositories require a Python version of *at least 3.8 and at most 3.10*.
For the provided build tooling the `python` and `pip` command must be linked to an
appropriate version, You can check the version and used installation with the

    python --version
    which python

commands. One option to manage Python versions is to use [pyenv](https://github.com/pyenv/pyenv).
Note, however, that `pyenv` doesn't work well together with anaconda. To detect if you
are using anaconda use the command above.
On OS X you can alternatively you install specific Python version using homebrew by installing

    brew install python@3.10

and adding it to your PATH variable, like

    export PATH="$(brew --prefix)/opt/python@3.10/libexec/bin:$PATH"

in `~/.zshrc` (see also their [their documentation](https://docs.brew.sh/Homebrew-and-Python)).

*Note* that using an alias for the `python` command in the shell configuration script does not
work as aliases are eventually not expanded if the shell is not in interactive mode.

##### Anaconda

If you are using anaconda the installation of some of the dependencies with pip can cause
issues. For this reason we recommend *not* to use anaconda to build and run the Leolanii
platform. As mentioned above, anaconda does not work well together with _pyenv_ as both use
the same mechanism to intercept the system PATH. If you are usually using anaconda to manage your
Python version, one option is to set the system Python installation to a version compatible with
Leolani and deactivate anaconda for the time working with Leolani. Note that anaconda typically
activates the _base_ environment by default when starting an interactive shell.

To set the system Python version with homebrew on Max OS X run

    brew install python@3.10

and follow the instructions in the output messages to prepend the PATH variable in your
`~/.zshrc` file and add your modifications _before_ the anaconda setup in `~/.zshrc`.

#### make

To build the application, `make` is used.

On OS X it is recommended to upgrade `make`. Since OS X doesn't use standard GNU
utils due their restrictive licence, default `make` on OS X is way outdated.

One option is to use homebrew:

    brew install make

and add the installed `gmake` command by adding

    PATH="$(brew --prefix)/opt/make/libexec/gnubin:$PATH"

to your `~/.zshrc`

#### Docker

[Docker](https://www.docker.com/) is a tool to run our applications or components in a
containerized runtime environment. To install it follow the instructions on their homepage
or use [Homebrew](https://formulae.brew.sh/cask/docker). *Note* that you need to use the
`--cask` option with Homebrew!

#### Java

To check if Java is installed on your system you can run

    java --version

in the command line. If this does not work, install Java, e.g. with

    brew install openjdk

#### Graph DB

Some components use GraphDB, to install it register on their
[homepage](https://www.ontotext.com/products/graphdb/download) and follow the provided instructions.

#### C compiler

Some dependencies require a C compiler to be installed. On Mac OS X you may need to install

        sudo xcode-select —install

If you encounter error messages regarding an invalid version of clang, you may need to reinstall
by first running

        sudo rm -rf /Library/Developer/CommandLineTools

followed by the installation command above.

#### Rust compiler

Some dependencies require a Rust compiler to be installed, follow the instructions on their
[homepage](https://www.rust-lang.org/tools/install) to install it.

#### System libraries

##### Audio

Python audio libraries may need portaudio to be installed, on Mac OS X you can use
[homebrew](https://formulae.brew.sh/formula/portaudio#default) to install it. To
figure out specific instructions regarding your hardware a simple internet search should
find you the answers.

Also *libsndfile* and *ffmpeg*  may need to be installed on your system.

Mac OS X the above can be installed with homebrew:

    brew install portaudio libsndfile ffmpeg

It is possible though that homebrew does not link the *libsndfile* properly, in this case follow
the instructions in this [stackoverflow](https://stackoverflow.com/questions/67973223/cannot-import-soundfile-mac) post
and pay attention to the output of homebrew. A likely fix is to add the following line to your
shell initialization script (`~/.zshrc`):

    export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"

##### Video

Pillow eventually needs additional system libraries to be installed, check the *External Libraries* section in their
[installation instructions](https://pillow.readthedocs.io/en/stable/installation/building-from-source.html#external-libraries)
if you run into errors related to Pillow.

## Development

To work on the development of a specific [application](#applications), start from the parent repository and follow the
steps described below. The description uses the [Eliza app](https://github.com/leolani/eliza-parent) as example.

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
[cltl-requirements](https://github.com/leolani/cltl-requirements), setup virtual environments for all components,
package them and publish the packages to [cltl-requirements](https://github.com/leolani/cltl-requirements) to make them
available to the application and other components.

To run the application follow the instructions in the [Eliza qparent](https://github.com/leolani/eliza-parent).

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
qthe application.

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

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any
contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->

## License

Distributed under the MIT License. See [`LICENSE`](https://github.com/leolani/cltl-combot/blob/main/LICENCE) for more
information.



<!-- CONTACT -->

## Authors

* [Taewoon Kim](https://tae898.github.io/)
* [Thomas Baier](https://www.linkedin.com/in/thomas-baier-05519030/)
* [Selene Báez Santamaría](https://selbaez.github.io/)
* [Piek Vossen](https://github.com/piekvossen)
