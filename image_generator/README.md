# Stable diffusion image generation

There is two demo apps

## 1. Streamlit demo app

You can have nice streamlit web application to try your requests.

Just run 
```bash
bash run_streamlit_demo.sh
```
and go to `localhost:80`.

## 2. Flask demo app

This is demo for web server.

Just run 
```bash
bash run_flask_demo.sh
```

and make a request:

```bash 
curl -X POST \
   0.0.0.0:80 \
   -H 'Content-Type: application/json' \
   -d '{"prompt": "Fox like creature steals candies in the fields cartoon style, detailed image background"}'
```
It will return `{"image": "<BASE64_ENCODED_IMAGE>"}`

Have fun.
