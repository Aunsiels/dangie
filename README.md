# DANGIE

## Website

The website can be accessed at the url [https://dangie.r2.enst.fr](https://dangie.r2.enst.fr).

## Run locally

### Prerequisites

To run the code, one must first install the libraries in requirements.txt

```bash
pip3 install -r requirements.txt
```

We recommand to use a virtual environment.

### Run With Flask

To run the code locally, one can either execute directly Flask with:

```bash
export FLASK_APP=launch_demo.py
flask run
```

Then, the website is accessible on localhost:5000.

### Run With Docker

With Docker installed, the website can be started with:

```bash
make build
docker build -t dangie .
docker stop dangie_website
docker rm dangie_website
docker run -p 8080:8080 -d --name dangie_website dangie
```

The website is then accesible on localhost:8080
