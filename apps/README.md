# Application scripts

This folder contains shell scripts to start applications distributed as Docker images.

## Running the applications

* Ensure eventually required infrastructure such as Docker Desktop or Graph DB is available.
* Execute the script, eventually adding necessary parameters.
* Check the `help` option of the script if needed.

### Modifications

Modifications to configurations or the Docker runtime should preferably be made by
creating a copy of the script and modifying the content of the script. This prevents
modifications to be overridden during the script execution.

## Working of the scirpts

The scripts are intended to run applications that are distributed as docker images.
A script should create a working directory that consists of the script name postfixed by
`_app` that will contain:

* A `docker-compose.yml` file to define the docker run configuration

  _This file will eventually cleared at each run of the script!_
* A `config/` folder where configuration files are created.

  _This folder is eventually cleared at each run of the script!_
* A `storage/` folder that contains data created by the application 
* Eventually a `credentials/` folder where credential files need to be placed if required
* Eventually a `venv/` folder if a local backend is created or any other local
  python application is started.

## Applications

| Script name               | Description                               | Options                 | Infra     | Docker image          |
|---------------------------|-------------------------------------------|-------------------------|-----------|-----------------------|
| leolani_whisper_8eeab3.sh | Full Leolani application with Whisper ASR | - Backend IP (optional) | - GraphDB | numblr/leolani:8eeab3 | 

