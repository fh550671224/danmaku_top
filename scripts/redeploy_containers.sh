export CRT_PATH=/home/ubuntu/crt/combined.crt
export KEY_PATH=/home/ubuntu/crt/tls.key

docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker-compose -f ../docker-compose.yml up -d