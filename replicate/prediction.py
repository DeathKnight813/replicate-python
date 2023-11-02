import re
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional, TypedDict, Union, overload

from typing_extensions import Unpack

from replicate.base_model import BaseModel
from replicate.collection import Collection
from replicate.exceptions import ModelError
from replicate.files import upload_file
from replicate.json import encode_json
from replicate.version import Version


class Prediction(BaseModel):
    """
    A prediction made by a model hosted on Replicate.
    """

    id: str
    """The unique ID of the prediction."""

    version: Optional[Version]
    """The version of the model used to create the prediction."""

    status: str
    """The status of the prediction."""

    input: Optional[Dict[str, Any]]
    """The input to the prediction."""

    output: Optional[Any]
    """The output of the prediction."""

    logs: Optional[str]
    """The logs of the prediction."""

    error: Optional[str]
    """The error encountered during the prediction, if any."""

    metrics: Optional[Dict[str, Any]]
    """Metrics for the prediction."""

    created_at: Optional[str]
    """When the prediction was created."""

    started_at: Optional[str]
    """When the prediction was started."""

    completed_at: Optional[str]
    """When the prediction was completed, if finished."""

    urls: Optional[Dict[str, str]]
    """
    URLs associated with the prediction.

    The following keys are available:
    - `get`: A URL to fetch the prediction.
    - `cancel`: A URL to cancel the prediction.
    """

    @dataclass
    class Progress:
        percentage: float
        """The percentage of the prediction that has completed."""

        current: int
        """The number of items that have been processed."""

        total: int
        """The total number of items to process."""

        _pattern = re.compile(
            r"^\s*(?P<percentage>\d+)%\s*\|.+?\|\s*(?P<current>\d+)\/(?P<total>\d+)"
        )

        @classmethod
        def parse(cls, logs: str) -> Optional["Prediction.Progress"]:
            """Parse the progress from the logs of a prediction."""

            lines = logs.split("\n")
            for i in reversed(range(len(lines))):
                line = lines[i].strip()
                if cls._pattern.match(line):
                    matches = cls._pattern.findall(line)
                    if len(matches) == 1:
                        percentage, current, total = map(int, matches[0])
                        return cls(percentage / 100.0, current, total)

            return None

    @property
    def progress(self) -> Optional[Progress]:
        """
        The progress of the prediction, if available.
        """
        if self.logs is None or self.logs == "":
            return None

        return Prediction.Progress.parse(self.logs)

    def wait(self) -> None:
        """
        Wait for prediction to finish.
        """
        while self.status not in ["succeeded", "failed", "canceled"]:
            time.sleep(self._client.poll_interval)  # pylint: disable=no-member
            self.reload()

    def output_iterator(self) -> Iterator[Any]:
        # TODO: check output is list
        previous_output = self.output or []
        while self.status not in ["succeeded", "failed", "canceled"]:
            output = self.output or []
            new_output = output[len(previous_output) :]
            yield from new_output
            previous_output = output
            time.sleep(self._client.poll_interval)  # pylint: disable=no-member
            self.reload()

        if self.status == "failed":
            raise ModelError(self.error)

        output = self.output or []
        new_output = output[len(previous_output) :]
        for output in new_output:
            yield output

    def cancel(self) -> None:
        """
        Cancels a running prediction.
        """
        self._client._request("POST", f"/v1/predictions/{self.id}/cancel")  # pylint: disable=no-member


class PredictionCollection(Collection):
    """
    Namespace for operations related to predictions.
    """

    class CreateParams(TypedDict):
        """Parameters for creating a prediction."""

        version: Union[Version, str]
        input: Dict[str, Any]
        webhook: Optional[str]
        webhook_completed: Optional[str]
        webhook_events_filter: Optional[List[str]]
        stream: Optional[bool]

    model = Prediction

    def list(self) -> List[Prediction]:
        """
        List your predictions.

        Returns:
            A list of prediction objects.
        """

        resp = self._client._request("GET", "/v1/predictions")
        # TODO: paginate
        predictions = resp.json()["results"]
        for prediction in predictions:
            # HACK: resolve this? make it lazy somehow?
            del prediction["version"]
        return [self.prepare_model(obj) for obj in predictions]

    def get(self, id: str) -> Prediction:
        """
        Get a prediction by ID.

        Args:
            id: The ID of the prediction.
        Returns:
            Prediction: The prediction object.
        """

        resp = self._client._request("GET", f"/v1/predictions/{id}")
        obj = resp.json()
        # HACK: resolve this? make it lazy somehow?
        del obj["version"]
        return self.prepare_model(obj)

    @overload
    def create(  # pylint: disable=arguments-differ disable=too-many-arguments
        self,
        version: Union[Version, str],
        input: Dict[str, Any],
        *,
        webhook: Optional[str] = None,
        webhook_completed: Optional[str] = None,
        webhook_events_filter: Optional[List[str]] = None,
        stream: Optional[bool] = None,
    ) -> Prediction:
        ...

    @overload
    def create(  # pylint: disable=arguments-differ disable=too-many-arguments
        self,
        *,
        version: Union[Version, str],
        input: Dict[str, Any],
        webhook: Optional[str] = None,
        webhook_completed: Optional[str] = None,
        webhook_events_filter: Optional[List[str]] = None,
        stream: Optional[bool] = None,
    ) -> Prediction:
        ...

    def create(
        self,
        *args,
        **kwargs: Unpack[CreateParams],  # type: ignore[misc]
    ) -> Prediction:
        """
        Create a new prediction for the specified model version.

        Args:
            version: The model version to use for the prediction.
            input: The input data for the prediction.
            webhook: The URL to receive a POST request with prediction updates.
            webhook_completed: The URL to receive a POST request when the prediction is completed.
            webhook_events_filter: List of events to trigger webhooks.
            stream: Set to True to enable streaming of prediction output.

        Returns:
            Prediction: The created prediction object.
        """

        # Support positional arguments for backwards compatibility
        version = args[0] if args else kwargs.get("version")
        if version is None:
            raise ValueError(
                "A version identifier must be provided as a positional or keyword argument."
            )

        input = args[1] if len(args) > 1 else kwargs.get("input")
        if input is None:
            raise ValueError(
                "An input must be provided as a positional or keyword argument."
            )

        body = {
            "version": version if isinstance(version, str) else version.id,
            "input": encode_json(input, upload_file=upload_file),
        }

        for key in ["webhook", "webhook_completed", "webhook_events_filter", "stream"]:
            value = kwargs.get(key)
            if value is not None:
                body[key] = value

        resp = self._client._request(
            "POST",
            "/v1/predictions",
            json=body,
        )
        obj = resp.json()
        if isinstance(version, Version):
            obj["version"] = version
        else:
            del obj["version"]

        return self.prepare_model(obj)
