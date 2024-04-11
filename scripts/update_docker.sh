docker build -t danmaku_top ../.
docker tag danmaku_top richard1227/danmaku_top
docker push richard1227/danmaku_top
docker pull richard1227/danmaku_top

docker pull richard1227/danmaku_top_frontend

docker pull redis
docker pull mongo
docker pull nginx