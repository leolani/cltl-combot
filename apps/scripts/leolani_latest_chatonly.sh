#!/bin/bash


app_dir="${0%.sh}_app"


if [[ "$*" == *"help"* ]]
then
  echo ""
  echo "Script to run the Leolani application without backend (only Chat UI)"
  echo ""
  echo "Usage: $0"
  echo ""
  echo "The script will create a folder called $app_dir in the directory"
  echo "where it is called and create configuration and docker-compose.yml files in there."
  echo "Those will be recreated each time. If you need to modify the configuration, make"
  echo "a copy of this script and perform the modification there."
  exit 0
fi


mkdir -p "$app_dir"
cd "$app_dir"

echo "Clean and setup directories"
rm -rf config

mkdir -p config storage credentials
mkdir -p storage/audio storage/image


#########################################
## Set the log level here
#########################################
loglevel="DEBUG"


echo "Setup logging on level $loglevel"

cat <<EOF > config/.logging.config
[loggers]
keys: root,werkzeug

[handlers]
keys: console

[formatters]
keys: pepperFormatter

[logger_root]
level: $loglevel
handlers: console

[logger_werkzeug]
level: $loglevel
handlers: console
qualname=werkzeug

[handler_console]
class: StreamHandler
level: NOTSET
formatter: pepperFormatter
args: (sys.stdout,)

[formatter_pepperFormatter]
format: %(asctime)s %(levelname)-8s %(name)-60s %(message)s
datefmt: %x %X
EOF


echo "Clean and setup configs"


cat <<EOF > config/DEFAULT
name: cltl-leolani-chatonly
EOF

cat <<EOF > config/cltl.backend.image
topic:
EOF

cat <<EOF > config/cltl.backend.mic
topic:
EOF

#########################################
## Change the GraphDB repository location here:
## where http://host.docker.internal:7200/ is the root URL of Graph DB
#########################################
cat <<EOF > config/cltl.backend
run_server: False
EOF

cat <<EOF > config/cltl.brain
address: http://host.docker.internal:7200/repositories/sandbox
EOF

cat <<EOF > config/cltl.entity_linking
address: http://host.docker.internal:7200/repositories/sandbox
EOF

cat <<EOF > config/cltl.emissor-data.event
topics: cltl.topic.scenario,
        cltl.topic.text_in, cltl.topic.text_out, cltl.topic.text_out_replier,
        cltl.topic.face_id, cltl.topic.speaker,
        cltl.topic.emotion, cltl.topic.dialogue_act,
        cltl.topic.nlp, cltl.topic.speaker
EOF

cat <<EOF > config/cltl.g2ky
implementation: verbal
EOF

cat <<EOF > config/cltl.vad
implementation:
EOF

cat <<EOF > config/cltl.asr
implementation:
EOF

cat <<EOF > config/cltl.object_recognition
implementation:
EOF

cat <<EOF > config/cltl.face_recognition
implementation:
EOF

cat <<EOF > config/cltl.face_emotion_recognition
implementation:
EOF

cat <<EOF > config/environment
EOF

#########################################
## Change triple extraction and reply generation settings here:
#########################################

#cat <<EOF > config/cltl.triple_extraction
#implementation: CFGAnalyzer
#EOF

#cat <<EOF > config/cltl.reply_generation
#utterance_types: question, statement, text_mention
#thought_options: _complement_conflict, _negation_conflicts, _statement_novelty, _entity_novelty, _subject_gaps, _complement_gaps, _overlaps, _trust
#randomness: 0.25
#EOF



echo "Clean and setup run configuration"

rm -f docker-compose.yml

cat <<EOF > docker-compose.yml
version: "3.9"

services:
  leolani:
    image: "numblr/leolani:latest"
    ports:
      - "8000:8000"
    volumes:
      - ./config:/cltl_k8_config
      - ./credentials:/credentials
      - ./storage:/leolani/cltl-leolani-app/py-app/storage
    extra_hosts:
      - "host.docker.internal:host-gateway"
    environment:
      - CLTL_LOGGING_CONFIG=/cltl_k8_config/.logging.config
EOF


echo "Run"
docker compose up
