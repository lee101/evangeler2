echo "please run pytest tests before deploying"
gcloud config set project evangelerapp

gsutil -m rsync -r ./static/css gs://static.netwrck.com/static/css
gsutil -m rsync -r ./static/img gs://static.netwrck.com/static/img
gsutil -m rsync -r ./static/evimg gs://static.netwrck.com/static/evimg
gsutil -m rsync -r ./static/js gs://static.netwrck.com/static/js

gcloud app deploy --project evangelerapp

# deploy index.yaml
# gcloud app deploy --project evangelerapp --no-promote index.yaml

