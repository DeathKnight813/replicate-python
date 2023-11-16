import json

import httpx
import pytest
import respx

from replicate.client import Client

router = respx.Router(base_url="https://api.replicate.com/v1")
router.route(
    method="POST",
    path="/deployments/test/model/predictions",
    name="deployments.predictions.create",
).mock(
    return_value=httpx.Response(
        201,
        json={
            "id": "p1",
            "model": "test/model",
            "version": "v1",
            "urls": {
                "get": "https://api.replicate.com/v1/predictions/p1",
                "cancel": "https://api.replicate.com/v1/predictions/p1/cancel",
            },
            "created_at": "2022-04-26T20:00:40.658234Z",
            "source": "api",
            "status": "processing",
            "input": {"text": "world"},
            "output": None,
            "error": None,
            "logs": "",
        },
    )
)
router.route(host="api.replicate.com").pass_through()


@pytest.mark.asyncio
@pytest.mark.parametrize("async_flag", [True, False])
async def test_deployment_predictions_create(async_flag):
    client = Client(
        api_token="test-token", transport=httpx.MockTransport(router.handler)
    )

    if async_flag:
        deployment = await client.deployments.async_get("test/model")

        prediction = await deployment.predictions.async_create(
            input={"text": "world"},
            webhook="https://example.com/webhook",
            webhook_events_filter=["completed"],
            stream=True,
        )
    else:
        deployment = client.deployments.get("test/model")

        prediction = deployment.predictions.create(
            input={"text": "world"},
            webhook="https://example.com/webhook",
            webhook_events_filter=["completed"],
            stream=True,
        )

    assert router["deployments.predictions.create"].called
    request = router["deployments.predictions.create"].calls[0].request
    request_body = json.loads(request.content)
    assert request_body["input"] == {"text": "world"}
    assert request_body["webhook"] == "https://example.com/webhook"
    assert request_body["webhook_events_filter"] == ["completed"]
    assert request_body["stream"] is True

    assert prediction.id == "p1"
    assert prediction.input == {"text": "world"}
