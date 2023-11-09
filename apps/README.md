# Leolani Applications

This folder contains various docker applications. To run the applications download the respective folder and follow
the instructions in the contained README.

To download a folder directly you can use on of the following options: 

* [Download directory](https://download-directory.github.io/)
* [DownGit](https://minhaskamal.github.io/DownGit/#/home)
* [SVN](https://subversion.apache.org/packages.html) (replace `<app_folder>` with the folder to download)

      svn export https://github.com/leolani/cltl-combot/trunk/apps/<app_folder>

## Applications

| Folder name                 | Description                                                                      | Infra                         | Docker image              |
|-----------------------------|----------------------------------------------------------------------------------|-------------------------------|---------------------------|
| leolani_local_latest        | Full Leolani application with Whisper ASR, local backend                         | GraphDB/Docker/Backend Server | numblr/leolani:latest     |
| leolani_robot_latest        | Full Leolani application with Whisper ASR, remote backend                        | GraphDB/Docker                | numblr/leolani:latest     |
| leolani_chatonly_latest     | Leolani application with Chat UI only                                            | GraphDB/Docker                | numblr/leolani:latest     |
| leolani_local_combot2023    | Full Leolani application with Whisper ASR, local backend for ComBot course 2023  | GraphDB/Docker/Backend Server | numblr/leolani:combot2023 |
| leolani_robot_combot2023    | Full Leolani application with Whisper ASR, remote backend for ComBot course 2023 | GraphDB/Docker                | numblr/leolani:combot2023 |
| leolani_chatonly_combot2023 | Leolani application with Chat UI only for ComBot course 2023                     | GraphDB/Docker                | numblr/leolani:combot2023 |
