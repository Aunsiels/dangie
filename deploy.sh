make build
docker build -t dangie .
docker stop dangie_website
docker rm dangie_website
docker run -p 8080:8080 -d --name dangie_website dangie