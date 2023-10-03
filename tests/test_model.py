import pytest

import replicate


@pytest.mark.vcr("models-get.yaml")
@pytest.mark.asyncio
async def test_models_get(mock_replicate_api_token):
    model = replicate.models.get("stability-ai/sdxl")

    assert model is not None
    assert model.username == "stability-ai"
    assert model.name == "sdxl"
