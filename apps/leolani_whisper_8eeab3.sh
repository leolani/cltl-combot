#!/bin/bash


app_dir="${0%.sh}_app"


if [[ "$*" == *"help"* ]]
then
  echo ""
  echo "Script to run the Leolani application"
  echo ""
  echo "Usage: $0 [IP address]"
  echo ""
  echo "where the IP address is the IP address of a remote backend server"
  echo "in the format xxx.xxx.xxx.xxx"
  echo "If no IP address is provided, a backend server will be started on the"
  echo "host machine and be used as backend for the application."
  echo ""
  echo "The script will create a folder called $app_dir in the directory"
  echo "where it is called and create configuration and docker-compose.yml files in there."
  echo "Those will be recreated each time. If you need to modify the configuration, make"
  echo "a copy of this script and perform the modification there."
  echo ""
  echo "If credentials are used, they must be put in the generated credentials/ folder."
  exit 0
fi


mkdir -p "$app_dir"
cd "$app_dir"

echo "Clean and setup directories"
rm -r config

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
name: cltl-leolani
EOF

#########################################
## Change the GraphDB repository location here:
## where http://host.docker.internal:7200/ is the root URL of Graph DB
#########################################
cat <<EOF > config/cltl.brain
address: http://host.docker.internal:7200/repositories/sandbox
EOF

cat <<EOF > config/cltl.entity_linking
address: http://host.docker.internal:7200/repositories/sandbox
EOF

cat <<EOF > config/cltl.face_recognition
implementation: proxy
EOF

cat <<EOF > config/cltl.face_recognition.proxy
start_infra: False
detector_url: http://face-recognition:10002/
age_gender_url: http://age-recognition:10003/
EOF

cat <<EOF > config/cltl.object_recognition
implementation: proxy
EOF

cat <<EOF > config/cltl.object_recognition.proxy
start_infra: False
detector_url: http://object-recognition:10004/
EOF

cat <<EOF > config/cltl.asr
implementation: whisper
EOF

cat <<EOF > config/environment
GOOGLE_APPLICATION_CREDENTIALS: /credentials/google_cloud_key.json
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

rm docker-compose.yml

cat <<EOF > docker-compose.yml
version: "3.9"

services:
  leolani:
    image: "numblr/leolani:8eeab3"
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
  face-recognition:
    image: "tae898/face-detection-recognition:latest"
    ports:
      - "10002:10002"
  object-recognition:
    image: "tae898/yolov5:latest"
    ports:
      - "10004:10004"
  age-recognition:
    image: "tae898/age-gender:latest"
    ports:
      - "10003:10003"
EOF


echo "Setup venv for server"

python -m venv venv
source venv/bin/activate
pip install "cltl-backend[host]"


if [[ "$*" == *"."* ]]
then
echo "Configure IP $robot_ip"

robot_ip="${@: -1}"

cat <<EOF > config/cltl.backend
run_server: False
server_image_url: http://$robot_ip:8000
server_audio_url: http://$robot_ip:8000
EOF

cat <<EOF > config/cltl.backend.text_output
remote_url: http://$robot_ip:8000
EOF

else
echo "Unset IP"

cat <<EOF > config/cltl.backend
run_server: False
server_image_url: http://host.docker.internal:8080/
server_audio_url: http://host.docker.internal:8080/
EOF

rm -f config/cltl.backend.text_output
fi


echo "Run"
source venv/bin/activate
docker compose up &


if [[ "$*" == *"."* ]]
then
  echo "Backend on Robot $robot_ip"
else
  echo "Start backend"
  leoserv --channels 1 --port 8080 --resolution VGA
fi

