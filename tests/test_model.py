import pytest

import replicate


@pytest.mark.vcr("models-get.yaml")
@pytest.mark.asyncio
@pytest.mark.parametrize("async_flag", [True, False])
async def test_models_get(async_flag):
    if async_flag:
        sdxl = await replicate.models.async_get("stability-ai/sdxl")
    else:
        sdxl = replicate.models.get("stability-ai/sdxl")

    assert sdxl is not None
    assert sdxl.owner == "stability-ai"
    assert sdxl.name == "sdxl"
    assert sdxl.visibility == "public"

    if async_flag:
        empty = await replicate.models.async_get("mattt/empty")
    else:
        empty = replicate.models.get("mattt/empty")

    assert empty.default_example is None


@pytest.mark.vcr("models-list.yaml")
@pytest.mark.asyncio
@pytest.mark.parametrize("async_flag", [True, False])
async def test_models_list(async_flag):
    if async_flag:
        models = await replicate.models.async_list()
    else:
        models = replicate.models.list()

    assert len(models) > 0
    assert models[0].owner is not None
    assert models[0].name is not None
    assert models[0].visibility == "public"


@pytest.mark.vcr("models-list__pagination.yaml")
@pytest.mark.asyncio
@pytest.mark.parametrize("async_flag", [True, False])
async def test_models_list_pagination(async_flag):
    if async_flag:
        page1 = await replicate.models.async_list()
    else:
        page1 = replicate.models.list()
    assert len(page1) > 0
    assert page1.next is not None

    if async_flag:
        page2 = await replicate.models.async_list(cursor=page1.next)
    else:
        page2 = replicate.models.list(cursor=page1.next)
    assert len(page2) > 0
    assert page2.previous is not None


@pytest.mark.vcr("models-create.yaml")
@pytest.mark.asyncio
@pytest.mark.parametrize("async_flag", [True, False])
async def test_models_create(async_flag):
    if async_flag:
        model = await replicate.models.async_create(
            owner="test",
            name="python-example",
            visibility="private",
            hardware="cpu",
            description="An example model",
        )
    else:
        model = replicate.models.create(
            owner="test",
            name="python-example",
            visibility="private",
            hardware="cpu",
            description="An example model",
        )

    assert model.owner == "test"
    assert model.name == "python-example"
    assert model.visibility == "private"


@pytest.mark.vcr("models-create.yaml")
@pytest.mark.asyncio
@pytest.mark.parametrize("async_flag", [True, False])
async def test_models_create_with_positional_arguments(async_flag):
    if async_flag:
        model = await replicate.models.async_create(
            "test",
            "python-example",
            visibility="private",
            hardware="cpu",
        )
    else:
        model = replicate.models.create(
            "test",
            "python-example",
            visibility="private",
            hardware="cpu",
        )

    assert model.owner == "test"
    assert model.name == "python-example"
    assert model.visibility == "private"
