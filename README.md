# CLTL Leolani Combot

CLTL Leolani Combot provides the framework for applications that implement human-robot interaction with conversation.

## About the Project

This is the successor of the [Leolani platform](https://github.com/leolani/pepper) with an improved modular architecture.

## Getting Started

### Applications

Clone one of the application parents from this project space:

* [Eliza app](https://github.com/leolani/eliza-parent)
* [Get to know you app](https://github.com/leolani/g2ky-parent)

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
and follow the steps described below. The description uses the Eliza app
as example.

### Check-out

To check out all code needed for the Eliza App, clone this repository including all submodules:

        git clone --recurse-submodules -j8 https://github.com/leolani/eliza-parent.git

### Workflow using PyCharm

1. Checkout the repository with submodules (see above).
1. Build the project running `make build` from the parent root. This will create virtual environments for all components
and build and install Python packages for each component.
1. Go to `File > Open` in PyCharm and select the `cltl-eliza-app` as new project in PyCharm. Later, PyCharm will list the workbench with this project name in `Recently Opened`.
1. To add the other components, go to `File > Open` again in PyCharm and select all other compoents. For each component choose `Attach` to add it
to the current workbench. The virtual environments created in step 2 will be used automatically by PyCharm.
1. Code changes in a single module do not require any special workflow, try to add unit tests to make sure the code works.
1. To make code changes visible across modules, `make build` **must** be run from the parent project to rebuild packages and update the individual
virtual environments of the components with the updated packages.
1. Commit and push the code changes in the individual modules as usual.
1. Create an application that configures and runs the components (see https://github.com/leolani/cltl-eliza-app for an example).
1. Commit the state of the submodules in the parent when the components of the application are in a consistent state.

#### Things to pay attention to

1. In the above workflow each component has its own virtual environment in the `venv/` folder, and this is respected by PyCharm. For this reason,
    - code becomes visible to other components only after running `make build`.
    - navigation in PyCharm will lead to the **module in the virtual environment,
     not to the original source**. Therefore, if you make changes there, they will
     be overriden during the next build. You will also get a warning from PyCharm
     if you try to edit those files.
    - for debugging breakpoints need to be set in the virtual environemnt. To achieve that navigate there from the module that is run in PyCharm (app
    component)

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
implement the subscription to one or multiple topics in the event bus.~~~~

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

The `cltl.combot.infra.di_container` moduel provides a simple utility to use
dependecy inject in the application. 

### Common libraries

To be added.

### Events based on EMISSOR

To be moved from `cltl-backend`.


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
