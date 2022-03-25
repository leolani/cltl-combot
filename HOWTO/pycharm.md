# Workflow using PyCharm

The following instructions use the [Eliza app](https://github.com/leolani/eliza-parent) as example:

1. Checkout the parent repository with submodules, see [Eliza app](https://github.com/leolani/eliza-parent).
2. Build the project running `make build` from the parent root. This will create virtual environments for all components
and build and install Python packages for each component.
3. Go to `File > Open` in PyCharm and select the `cltl-eliza-app` as new project in PyCharm. Later, PyCharm will list the workbench with this project name in `Recently Opened`.
4. To add the other components, go to `File > Open` again in PyCharm and select all other componets. For each component choose `Attach` to add it
to the current workbench. The virtual environments created in step 2 should be used automatically by PyCharm. This can 
be checked in the settings under `Settings>Project>Project Interpreter`. If this fails, the Python interpreter of the
individual components must be set in the settings to the virtual environments of the individual components.   
5. Code changes in a single module do not require any special workflow, try to add unit tests to make sure the code works.
6. To make code changes visible across modules, `make build` **must** be run from the parent project to rebuild packages and update the individual
virtual environments of the components with the updated packages.
7. Commit and push the code changes in the individual modules as usual.
8. Create an application that configures and runs the components (see the [Eliza app](https://github.com/leolani/cltl-eliza-app) for an example).
9. Commit the state of the submodules in the parent when the components of the application are in a consistent state.

## Things to pay attention to

1. In the above workflow each component has its own virtual environment in the `venv/` folder, and this is respected by PyCharm. For this reason,
    - code becomes visible to other components only after running `make build`.
    - navigation in PyCharm will lead to the **module in the virtual environment,
     not to the original source**. Therefore, if you make changes there, they will
     be overriden during the next build. You will also get a warning from PyCharm
     if you try to edit those files.
    - for debugging breakpoints need to be set in the virtual environemnt. To achieve that navigate there from the module that is run in PyCharm (app
    component)
  
    Alternatively, it is possible to make the code of a component directly visible to other components by setting the
    component dependencies in the PyCharm settings, however, that is tedious to setup.
