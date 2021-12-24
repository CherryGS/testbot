sudo docker build . \
    -t cherrygs/testbot:dev
sudo /usr/local/bin/docker-compose stop
sudo /usr/local/bin/docker-compose up -d
