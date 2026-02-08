import os
from gradient import Gradient

client = Gradient(
    model_access_key=os.getenv("GRADIENT_ACCESS_KEY"),
)
response = client.images.generate(
    prompt="A cute baby sea otter floating on its back in calm blue water",
)
print(response.created)
