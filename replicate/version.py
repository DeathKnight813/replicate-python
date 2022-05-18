import datetime
from typing import Any, Iterator, List, Union

from replicate.base_model import BaseModel
from replicate.collection import Collection
from replicate.exceptions import ModelError


class Version(BaseModel):
    id: str
    created_at: datetime.datetime
    cog_version: str
    openapi_schema: Any

    def predict(self, **kwargs) -> Union[Any, Iterator[Any]]:
        # TODO: support args
        prediction = self._client.predictions.create(version=self, input=kwargs)
        # Return an iterator of the output
        # FIXME: might just be a list, not an iterator. I wonder if we should differentiate?
        if (
            self.openapi_schema["components"]["schemas"]["Output"].get("type")
            == "array"
        ):
            return prediction.output_iterator()

        prediction.wait()
        if prediction.status == "failed":
            raise ModelError(prediction.error)
        return prediction.output


class VersionCollection(Collection):
    model = Version

    def __init__(self, client, model):
        super().__init__(client=client)
        self._model = model

    # doesn't exist yet
    def get(self, id: str) -> Version:
        """
        Get a specific version.
        """
        resp = self._client._get(f"/v1/versions/{id}")
        resp.raise_for_status()
        return self.prepare_model(resp.json())

    def list(self) -> List[Version]:
        """
        Return a list of all versions for a model.
        """
        resp = self._client._get(
            f"/v1/models/{self._model.username}/{self._model.name}/versions"
        )
        resp.raise_for_status()
        return [self.prepare_model(obj) for obj in resp.json()["results"]]
