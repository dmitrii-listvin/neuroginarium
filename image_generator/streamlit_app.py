from contextlib import ExitStack
from pathlib import Path
from typing import ContextManager

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from stable_diffusion import StableDiffusion

output_path = Path("output")

plt_rc_params = {
    "font.family": "monospace",
    "font.size": 20,
    "savefig.facecolor": (14 / 255, 17 / 255, 22 / 255),
}
plt_style = "dark_background"


class FigureManager(ContextManager):
    def __init__(self, figure: plt.Figure):
        self._figure = figure

    def __enter__(self):
        return self._figure

    def __exit__(self, type, value, traceback):  # noqa
        plt.close(self._figure)


@st.experimental_singleton
def load_model():
    return StableDiffusion()


def get_streamlit_controls():
    form = st.sidebar.form(key="input")
    submit_button = form.form_submit_button(label="Generate")
    fill_black_flag = form.checkbox("Just fill black")
    text_input = form.text_input(
        "Prompt for stable diffusion",
        value="Fox like creature steals candies in the fields cartoon style, detailed image background",
    )
    return submit_button, fill_black_flag, text_input


def save_output(file_name, generated_image):
    try:
        last_index = max(int(file.name.split("__")[0]) for file in output_path.glob("*"))
    except ValueError:
        last_index = -1
    last_index = last_index + 1

    generated_image_path = output_path / f"{last_index:04d}__{Path(file_name).stem}_gen.png"
    plt.imsave(generated_image_path, generated_image)

    return generated_image_path


def run_streamlit():
    (
        submit_button,
        fill_black_flag,
        text_input,
    ) = get_streamlit_controls()

    if not submit_button:
        st.markdown("### Use left panel to start generation")
        return

    st.markdown("### Stable diffusion image output")

    if fill_black_flag:
        generated_image = np.zeros((200, 200, 3), dtype=np.uint8)
    else:
        model = load_model()
        with st.spinner("Inferring stable diffusion (~15 sec)"):
            generated_image = model.generate(text_input)

    with st.spinner("Saving..."):
        image_file_path = save_output("image", generated_image)

    st.download_button(
        label="Download generated image",
        data=image_file_path.read_bytes(),
        file_name=image_file_path.name,
        mime="application/octet-stream",
    )
    with st.spinner("Visualizing..."):
        fig = plt.figure(figsize=(15, 15))
        with ExitStack() as context:
            context.enter_context(FigureManager(fig))
            context.enter_context(plt.style.context(plt_style))
            context.enter_context(plt.rc_context(plt_rc_params))
            plt.imshow(generated_image)
            plt.xticks(list(range(0, generated_image.shape[1], 100)))
            plt.yticks(list(range(0, generated_image.shape[0], 100)))
            plt.tight_layout(pad=0.0)
            plt.grid()
            st.pyplot(fig)


if __name__ == "__main__":
    st.set_page_config(layout="centered")
    output_path.mkdir(exist_ok=True, parents=True)
    run_streamlit()
