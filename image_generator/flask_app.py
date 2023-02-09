import base64
from io import BytesIO

from flask import Flask, request
from matplotlib.image import imsave

from stable_diffusion import StableDiffusion

model: StableDiffusion = None


def load_model():
    global model
    model = StableDiffusion()


app = Flask(__name__)


@app.route('/', methods=['POST'])
def get_prediction():
    # Works only for a single sample
    if request.method != 'POST':
        return

    data = request.get_json()  # Get data posted as a json
    prompt = data["prompt"]
    image = model.generate(prompt)

    with BytesIO() as buffer:
        imsave(buffer, image)
        buffer.seek(0)

        response = {
            "image": base64.b64encode(buffer.read()).decode()
        }
    return response


if __name__ == '__main__':
    load_model()  # load model at the beginning once only
    app.run(host='0.0.0.0', port=80)
