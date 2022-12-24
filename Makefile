mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
mkfile_dir := $(dir $(mkfile_path))

all: build-frontend build-backend run-all-docker
	echo Starting All

build-svelte: # builds the .svelte file to html
	cd $(mkfile_dir)/frontend; npm run build;


# build docker images for food-buddy
build-frontend:
	docker build --network=host -t catsmao/pve-vdi-frontend $(mkfile_dir)/frontend

build-backend:
	docker build --network=host -t catsmao/pve-vdi-backend $(mkfile_dir)/backend

build-frontend-no-cache:
	docker build --no-cache --network=host -t catsmao/pve-vdi-frontend $(mkfile_dir)/frontend

build-backend-no-cache:
	docker build --no-cache --network=host -t catsmao/pve-vdi-backend $(mkfile_dir)/backend

build-docker:build-frontend-no-cache build-backend-no-cache


# Docker Commands
push-dockers:
	docker push catsmao/pve-vdi-frontend:latest
	docker push catsmao/pve-vdi-backend:latest

run-frontend:
	 docker run -it --rm -d -p 3000:3000 --name frontend catsmao/pve-vdi-frontend

run-backend:
	 docker run -it --rm -d -p 8000:8000 --name backend catsmao/pve-vdi-backend

run-all-docker:
	docker-compose up -d

stop-all-docker:
	docker-compose down


# Runs dev server for food-buddy
svelte-dev:
	cd $(mkfile_dir)/frontend; npm run dev;

flask-dev:
	cd $(mkfile_dir)/backend; venv/bin/python -m flask run


svelte-test-generate: # Open a code generator to test svelte code
	npx playwright codegen pve-vdi.localhost

svelte-test:
	cd $(mkfile_dir)/frontend; npm run test;
