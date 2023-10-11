# Leolani application with Chat Interface only

## Configuration

### Logging

The logging of the application is configured in _config/.logging.config_. In particular the log level can be set in this
file in the `[logger_root]` section.

### Application

The _config/_ folder contains configuration of the application. Each file in this directory corresponds to the section
matching the file name in the [_default.config_](https://github.com/leolani/cltl-leolani-app/tree/main/py-app/config)
of the Leolani Python application and each key present in the file overrides the same key in that section.

#### Graph DB respository

The Graph DB respository is configured in the two places (note that the host machine is accessable under `host.docker.internal`
from within the docker contaiener):

1. _config/cltl.brain_
   * address: http://host.docker.internal:7200/repositories/sandbox
2. _config/cltl.entity_linking_
   * address: http://host.docker.internal:7200/repositories/sandbox

## Running the application

### Prerequisites

Install
1. [GraphDB](https://www.ontotext.com/products/graphdb/download),
2. [Docker](https://www.docker.com/).

### Setup

1. Ensure all folders are accessible, e.g. on Mac OS X run 
       
       chmod -R 775 .

2. Adjust the configurations if necessary.
3. Start Graph DB.
4. Start the Leolani Backend Server on the Robot.

### Run the Leolani application

1. Ensure you have the lastest version of the docker images (this step can be skipped)
        
       docker compose pull

2. Start the application by running (see also [docker compose](https://docs.docker.com/compose/))

       docker compose up -d

3. Stop the application

       docker compose down
