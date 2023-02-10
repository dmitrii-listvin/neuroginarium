# neuroginarium

# run locally
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
    url: "https://f784-87-228-220-167.eu.ngrok.io/"
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