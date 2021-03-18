IMAGE_NAME="stream4good/imdb_company_mapper"
VERSION=$(shell git describe --tags)
VERSION_MAJOR=$(shell git describe --tags|sed -rn 's/([0-9]+)\..*/\1/p')
VERSION_MAJOR_MINOR=$(shell git describe --tags|sed -rn 's/([0-9]+\.[0-9]+)\..*/\1/p')
docker-build-testing:
	docker build . -t $(IMAGE_NAME):testing
docker-push-testing:
	docker push $(IMAGE_NAME):testing
docker-build-release:
	docker build . -t $(IMAGE_NAME):$(VERSION)
docker-push-release:
	docker tag $(IMAGE_NAME):$(VERSION) $(IMAGE_NAME):$(VERSION_MAJOR)
	docker tag $(IMAGE_NAME):$(VERSION) $(IMAGE_NAME):$(VERSION_MAJOR_MINOR)
	docker push $(IMAGE_NAME):$(VERSION)
	docker push $(IMAGE_NAME):$(VERSION_MAJOR)
	docker push $(IMAGE_NAME):$(VERSION_MAJOR_MINOR)

dev-bootstrap-db: #clean and re-create sqlite db from model
	rm -rf app/app/app.db app/migrations
	cd app && FLASK_APP=app.main flask db init &&  FLASK_APP=app.main flask db migrate && FLASK_APP=app.main flask db upgrade
dev-run:
	cd app && API_ROOT=http://localhost:5000 FLASK_ENV=development FLASK_APP=app.main flask run
	
prod-bootstrap-db: 
	rm -rf app/app/app.db app/migrations
	cd app && SQLALCHEMY_DATABASE_URI=${SQLALCHEMY_DATABASE_URI} APP_ENV=production FLASK_APP=app.main flask db init &&  SQLALCHEMY_DATABASE_URI=${SQLALCHEMY_DATABASE_URI} APP_ENV=production FLASK_APP=app.main flask db migrate && SQLALCHEMY_DATABASE_URI=${SQLALCHEMY_DATABASE_URI} APP_ENV=production FLASK_APP=app.main flask db upgrade



