import re
from typing import Any, Dict, List, Optional, TypedDict, Union

from typing_extensions import NotRequired, Unpack, overload

from replicate.base_model import BaseModel
from replicate.collection import Collection
from replicate.exceptions import ReplicateException
from replicate.files import upload_file
from replicate.json import encode_json
from replicate.version import Version


class Training(BaseModel):
    """
    A training made for a model hosted on Replicate.
    """

    id: str
    """The unique ID of the training."""

    version: Optional[Version]
    """The version of the model used to create the training."""

    destination: Optional[str]
    """The model destination of the training."""

    status: str
    """The status of the training."""

    input: Optional[Dict[str, Any]]
    """The input to the training."""

    output: Optional[Any]
    """The output of the training."""

    logs: Optional[str]
    """The logs of the training."""

    error: Optional[str]
    """The error encountered during the training, if any."""

    created_at: Optional[str]
    """When the training was created."""

    started_at: Optional[str]
    """When the training was started."""

    completed_at: Optional[str]
    """When the training was completed, if finished."""

    urls: Optional[Dict[str, str]]
    """
    URLs associated with the training.

    The following keys are available:
    - `get`: A URL to fetch the training.
    - `cancel`: A URL to cancel the training.
    """

    def cancel(self) -> None:
        """Cancel a running training"""
        self._client._request("POST", f"/v1/trainings/{self.id}/cancel")  # pylint: disable=no-member


class TrainingCollection(Collection):
    """
    Namespace for operations related to trainings.
    """

    model = Training

    class CreateParams(TypedDict):
        """Parameters for creating a prediction."""

        version: Union[Version, str]
        destination: str
        input: Dict[str, Any]
        webhook: NotRequired[str]
        webhook_completed: NotRequired[str]
        webhook_events_filter: NotRequired[List[str]]

    def list(self) -> List[Training]:
        """
        List your trainings.

        Returns:
            List[Training]: A list of training objects.
        """

        resp = self._client._request("GET", "/v1/trainings")
        # TODO: paginate
        trainings = resp.json()["results"]
        for training in trainings:
            # HACK: resolve this? make it lazy somehow?
            del training["version"]
        return [self.prepare_model(obj) for obj in trainings]

    def get(self, id: str) -> Training:
        """
        Get a training by ID.

        Args:
            id: The ID of the training.
        Returns:
            Training: The training object.
        """

        resp = self._client._request(
            "GET",
            f"/v1/trainings/{id}",
        )
        obj = resp.json()
        # HACK: resolve this? make it lazy somehow?
        del obj["version"]
        return self.prepare_model(obj)

    @overload
    def create(  # pylint: disable=arguments-differ disable=too-many-arguments
        self,
        version: Union[Version, str],
        input: Dict[str, Any],
        destination: str,
        *,
        webhook: Optional[str] = None,
        webhook_completed: Optional[str] = None,
        webhook_events_filter: Optional[List[str]] = None,
    ) -> Training:
        ...

    @overload
    def create(  # pylint: disable=arguments-differ disable=too-many-arguments
        self,
        *,
        version: Union[Version, str],
        input: Dict[str, Any],
        destination: str,
        webhook: Optional[str] = None,
        webhook_completed: Optional[str] = None,
        webhook_events_filter: Optional[List[str]] = None,
    ) -> Training:
        ...

    def create(
        self,
        *args,
        **kwargs: Unpack[CreateParams],  # type: ignore[misc]
    ) -> Training:
        """
        Create a new training using the specified model version as a base.

        Args:
            version: The ID of the base model version that you're using to train a new model version.
            input: The input to the training.
            destination: The desired model to push to in the format `{owner}/{model_name}`. This should be an existing model owned by the user or organization making the API request.
            webhook: The URL to send a POST request to when the training is completed. Defaults to None.
            webhook_completed: The URL to receive a POST request when the prediction is completed.
            webhook_events_filter: The events to send to the webhook. Defaults to None.
        Returns:
            The training object.
        """

        # Support positional arguments for backwards compatibility
        version = args[0] if args else kwargs.get("version")
        if version is None:
            raise ValueError(
                "A version identifier must be provided as a positional or keyword argument."
            )

        destination = args[1] if len(args) > 1 else kwargs.get("destination")
        if destination is None:
            raise ValueError(
                "A destination must be provided as a positional or keyword argument."
            )

        input = args[2] if len(args) > 2 else kwargs.get("input")
        if input is None:
            raise ValueError(
                "An input must be provided as a positional or keyword argument."
            )

        body = {
            "input": encode_json(input, upload_file=upload_file),
            "destination": destination,
        }

        for key in ["webhook", "webhook_completed", "webhook_events_filter"]:
            value = kwargs.get(key)
            if value is not None:
                body[key] = value

        # Split version in format "username/model_name:version_id"
        match = re.match(
            r"^(?P<username>[^/]+)/(?P<model_name>[^:]+):(?P<version_id>.+)$",
            version.id if isinstance(version, Version) else version,
        )
        if not match:
            raise ReplicateException(
                "version must be in format username/model_name:version_id"
            )
        username = match.group("username")
        model_name = match.group("model_name")
        version_id = match.group("version_id")

        resp = self._client._request(
            "POST",
            f"/v1/models/{username}/{model_name}/versions/{version_id}/trainings",
            json=body,
        )
        obj = resp.json()
        del obj["version"]
        return self.prepare_model(obj)
