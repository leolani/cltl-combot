# Working with _git submodule_

The [git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules) system allows to include a git repository as a
sub-folder in another *git* repository. In the parent *git* repository a submodule is committed with a specific revision.
A good overview of *git* submodules is given in the link above, in the following find a short summary of the workflow.


## Cloning with submodules

Clone a repository with submodules:

    git clone --recurse-submodules -j8 https://github.com/leolani/eliza-parent.git

Cloning without `--recurse-submodules` will only create the subdirectories. In this case, initialize the submodules

    git submodule init

registers the submodule and initializes the local configuration (?). Then

    git submodule update

will update the content of the submodule. This can be combined into

    git submodule update --init --recursiv


## Status of submodules 

To check the status of the submodules, the *makefile* used in the application parents has a target to run git status on
each submodule
    make git-status

Other useful commands to show the status of the submodules are

    git submodule
    git submodule summary
    git diff --submodule
    git submodule foreach 'git log -1'


### Pull upstream state of the parent

    git pull --recurse-submodules

which is equivalent to

    git pull
    git submodule update --init --recursive

Local changes in submodules can be stashed by

    git submodule foreach 'git stash'
    # run update
    git submodule foreach 'git stash pop'

To revert to the parent state, discarding all local changes, run

    git checkout --recurse-submodules -- .


## Pull upstream changes of submodules

To pull changes for all submodules from their remote repositories run

    git submodule update --remote

This will update all submodules to the branch head of the branch configured in `.gitmodules`, or `master` by default.

Branches for submodules are configured if they are added with the `-b` option, or added lateer by running 

    git submodule set-branch --branch <branch_name> -- <submodule_path>


## Commit and push parent

To see commits in submodules that are not committed in the parent, run

    git diff --submodule

To push the parent and make sure all commits referenced by the parent are pushed in submodules run  

    git push --recurse-submodules=on-demand

from the parent.

If the above does not work, make sure each submodule's HEAD is on the right branch and the branch is
tracking by looking at the output of

    git submodule foreach 'git branch -vv'

The output for each module should have an asterix to mark the active branch and
the remote in square brackets, like

    Entering 'cltl-backend-naoqi'
    * main 3fd3fd5 [origin/main] Update README

if not, set the branch to the current head and set the branch to track the
respective upstream branch:

    git submodule foreach 'git checkout -B main'
    git branch -u origin/main

Push all submodules

    git submodule foreach 'git push'


## Fork an application

To create a fork of a whole application, it is not enough to fork tne parent repository, as the components
are *git* repositories on their own. Therefore, also the component repositories that will be changed in the
fork need to be forked by themselves. Components that will not be changed in the fork do not need to be forked.
The necessary steps are:

* Fork the parent repository, e.g. [eliza-parent](https://github.com/leolani/eliza-parent)
* Checkout the forked parent
* Fork each component repository that you want to change
* In the checked out parent fork, for each component run
  
        git submodule set-url <MODULE_NAME> <REMOTE_MODULE_FORK_URL>
 