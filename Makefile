build:
	docker build -t us.gcr.io/GCP_PROJECT_ID/gateway:0.1.0 ./gateway-server
deploy:
	docker push us.gcr.io/GCP_PROJECT_ID/gateway:0.1.0
	helm upgrade --set image.tag=0.1.0 --install reach ./reach/
