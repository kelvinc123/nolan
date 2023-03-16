# pull mongo image
docker pull mongo

# create container
docker stop mongo_nolan
docker rm mongo_nolan
docker create -it --name mongo_nolan -p 5100:27017 mongo

# run container
docker start mongo_nolan