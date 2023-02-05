# neuroginarium

# run locally
Create config.yml in root directory.
Write bot token there:
```
bot_token: "YOUR_TOKEN"
generation_choices_cnt: 4
image_generation:
  image_getter_class: "RandomImageGetter"
  image_height: 350
  image_width: 250
file_system:
  image_storage_class: "LocalImageStorage"
  s3:
    ak: "YOUR_AK"
    sk: "YOUR_SK"
    bucket: "YOUR_BUCKET"
  local:
    base_path: "decks"
```