import pytest

import replicate


@pytest.mark.vcr("predictions-create.yaml")
@pytest.mark.asyncio
async def test_predictions_create(mock_replicate_api_token):
    input = {
        "prompt": "a studio photo of a rainbow colored corgi",
        "width": 512,
        "height": 512,
        "seed": 42069,
    }

    model = replicate.models.get("stability-ai/sdxl")
    version = model.versions.get(
        "a00d0b7dcbb9c3fbb34ba87d2d5b46c56969c84a628bf778a7fdaec30b1b99c5"
    )
    prediction = replicate.predictions.create(
        version=version,
        input=input,
    )

    assert prediction.id is not None
    assert prediction.version == version
    assert prediction.status == "starting"


@pytest.mark.vcr("predictions-get.yaml")
@pytest.mark.asyncio
async def test_predictions_get(mock_replicate_api_token):
    id = "vgcm4plb7tgzlyznry5d5jkgvu"

    prediction = replicate.predictions.get(id)

    assert prediction.id == id


@pytest.mark.vcr("predictions-cancel.yaml")
@pytest.mark.asyncio
async def test_predictions_cancel(mock_replicate_api_token):
    input = {
        "prompt": "a studio photo of a rainbow colored corgi",
        "width": 512,
        "height": 512,
        "seed": 42069,
    }

    model = replicate.models.get("stability-ai/sdxl")
    version = model.versions.get(
        "a00d0b7dcbb9c3fbb34ba87d2d5b46c56969c84a628bf778a7fdaec30b1b99c5"
    )
    prediction = replicate.predictions.create(
        version=version,
        input=input,
    )

    # id = prediction.id
    assert prediction.status == "starting"

    # prediction = replicate.predictions.cancel(prediction)
    prediction.cancel()


@pytest.mark.vcr("predictions-stream.yaml")
@pytest.mark.asyncio
async def test_predictions_stream(mock_replicate_api_token):
    input = {
        "prompt": "write a sonnet about camelids",
    }

    model = replicate.models.get("meta/llama-2-70b-chat")
    version = model.versions.get(
        "02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3"
    )
    prediction = replicate.predictions.create(
        version=version,
        input=input,
        stream=True,
    )

    assert prediction.id is not None
    assert prediction.version == version
    assert prediction.status == "starting"
    assert prediction.urls["stream"] is not None


# @responses.activate
# def test_stream():
#     client = create_client()
#     version = create_version(client)

#     rsp = responses.post(
#         "https://api.replicate.com/v1/predictions",
#         match=[
#             matchers.json_params_matcher(
#                 {
#                     "version": "v1",
#                     "input": {"text": "world"},
#                     "stream": "true",
#                 }
#             ),
#         ],
#         json={
#             "id": "p1",
#             "version": "v1",
#             "urls": {
#                 "get": "https://api.replicate.com/v1/predictions/p1",
#                 "cancel": "https://api.replicate.com/v1/predictions/p1/cancel",
#                 "stream": "https://streaming.api.replicate.com/v1/predictions/p1",
#             },
#             "created_at": "2022-04-26T20:00:40.658234Z",
#             "completed_at": "2022-04-26T20:02:27.648305Z",
#             "source": "api",
#             "status": "processing",
#             "input": {"text": "world"},
#             "output": None,
#             "error": None,
#             "logs": "",
#         },
#     )

#     prediction = client.predictions.create(
#         version=version,
#         input={"text": "world"},
#         stream=True,
#     )

#     assert rsp.call_count == 1

#     assert (
#         prediction.urls["stream"]
#         == "https://streaming.api.replicate.com/v1/predictions/p1"
#     )


# @responses.activate
# def test_async_timings():
#     client = create_client()
#     version = create_version(client)

#     responses.post(
#         "https://api.replicate.com/v1/predictions",
#         match=[
#             matchers.json_params_matcher(
#                 {
#                     "version": "v1",
#                     "input": {"text": "hello"},
#                     "webhook_completed": "https://example.com/webhook",
#                 }
#             ),
#         ],
#         json={
#             "id": "p1",
#             "version": "v1",
#             "urls": {
#                 "get": "https://api.replicate.com/v1/predictions/p1",
#                 "cancel": "https://api.replicate.com/v1/predictions/p1/cancel",
#             },
#             "created_at": "2022-04-26T20:00:40.658234Z",
#             "source": "api",
#             "status": "processing",
#             "input": {"text": "hello"},
#             "output": None,
#             "error": None,
#             "logs": "",
#         },
#     )

#     responses.get(
#         "https://api.replicate.com/v1/predictions/p1",
#         json={
#             "id": "p1",
#             "version": "v1",
#             "urls": {
#                 "get": "https://api.replicate.com/v1/predictions/p1",
#                 "cancel": "https://api.replicate.com/v1/predictions/p1/cancel",
#             },
#             "created_at": "2022-04-26T20:00:40.658234Z",
#             "completed_at": "2022-04-26T20:02:27.648305Z",
#             "source": "api",
#             "status": "succeeded",
#             "input": {"text": "hello"},
#             "output": "hello world",
#             "error": None,
#             "logs": "",
#             "metrics": {
#                 "predict_time": 1.2345,
#             },
#         },
#     )

#     prediction = client.predictions.create(
#         version=version,
#         input={"text": "hello"},
#         webhook_completed="https://example.com/webhook",
#     )

#     assert prediction.created_at == "2022-04-26T20:00:40.658234Z"
#     assert prediction.completed_at is None
#     assert prediction.output is None
#     assert prediction.urls["get"] == "https://api.replicate.com/v1/predictions/p1"
#     prediction.wait()
#     assert prediction.created_at == "2022-04-26T20:00:40.658234Z"
#     assert prediction.completed_at == "2022-04-26T20:02:27.648305Z"
#     assert prediction.output == "hello world"
#     assert prediction.metrics["predict_time"] == 1.2345


# def test_prediction_progress():
#     client = create_client()
#     version = create_version(client)
#     prediction = Prediction(
#         id="ufawqhfynnddngldkgtslldrkq", version=version, status="starting"
#     )

#     lines = [
#         "Using seed: 12345",
#         "0%|          | 0/5 [00:00<?, ?it/s]",
#         "20%|██        | 1/5 [00:00<00:01, 21.38it/s]",
#         "40%|████▍     | 2/5 [00:01<00:01, 22.46it/s]",
#         "60%|████▍     | 3/5 [00:01<00:01, 22.46it/s]",
#         "80%|████████  | 4/5 [00:01<00:00, 22.86it/s]",
#         "100%|██████████| 5/5 [00:02<00:00, 22.26it/s]",
#     ]
#     logs = ""

#     for i, line in enumerate(lines):
#         logs += "\n" + line
#         prediction.logs = logs

#         progress = prediction.progress

#         if i == 0:
#             prediction.status = "processing"
#             assert progress is None
#         elif i == 1:
#             assert progress is not None
#             assert progress.current == 0
#             assert progress.total == 5
#             assert progress.percentage == 0.0
#         elif i == 2:
#             assert progress is not None
#             assert progress.current == 1
#             assert progress.total == 5
#             assert progress.percentage == 0.2
#         elif i == 3:
#             assert progress is not None
#             assert progress.current == 2
#             assert progress.total == 5
#             assert progress.percentage == 0.4
#         elif i == 4:
#             assert progress is not None
#             assert progress.current == 3
#             assert progress.total == 5
#             assert progress.percentage == 0.6
#         elif i == 5:
#             assert progress is not None
#             assert progress.current == 4
#             assert progress.total == 5
#             assert progress.percentage == 0.8
#         elif i == 6:
#             assert progress is not None
#             prediction.status = "succeeded"
#             assert progress.current == 5
#             assert progress.total == 5
#             assert progress.percentage == 1.0
