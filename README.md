# Neuroginarium

# Run locally
Create config.yml in root directory.
Write bot token there:
```
bot_token: "TOKEN"
generation_choices_cnt: 2
image_generation:
  image_getter_class: "UrlImageGetter"
  RandomImageGetter:
    height: 350
    width: 350
  UrlImageGetter:
    url: "URL"
file_system:
  image_storage_class: "LocalImageStorage"
  S3ImageStorage:
    ak: "AK"
    sk: "SK"
    bucket: "neuroginarium"
  LocalImageStorage:
    base_path: "decks"
database:
  type: "sqlite"
  sqlite:
    filename: "database.sqlite"
    create_db: True
  postgres:
    user: ""
    password: ""
    host: ""
    database: ""
```

run `python main.py config.yml`

# Release

## Pre-setup
1. Install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
2. Create neuroginarium_dev aws profile (ask Dima for credentials):
    ```
    aws configure --profile neuroginarium_dev
    ```
3. Create prod_config.yml in root directory with prod bot token, s3 storage and prod Postgres database (or ask Dima for one)

## Release steps
1. Increment versions in build_container.sh and upload_container.sh
2. Run `sh build_container.sh`
3. Run `sh upload_container.sh`

# Deploy
Now done manually by Dima via AWS console; Later will make via Github Actions.