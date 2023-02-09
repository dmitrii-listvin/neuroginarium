import numpy as np
from diffusers import DPMSolverMultistepScheduler, StableDiffusionPipeline
import torch


class StableDiffusion:
    def __init__(self, model_id: str = "stabilityai/stable-diffusion-2-1"):
        self._model = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
        self._model.scheduler = DPMSolverMultistepScheduler.from_config(self._model.scheduler.config)
        self._model = self._model.to("cuda")

    def generate(self, prompt: str) -> np.ndarray:
        generated_image = self._model(prompt).images[0]
        return np.array(generated_image)
