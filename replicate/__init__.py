from .__about__ import __version__
from .client import Client

default_client = Client()
run = default_client.run
models = default_client.models
predictions = default_client.predictions
