"""Define the heos source module."""
from typing import Dict, Optional, Sequence  # pylint: disable=unused-import

from . import const


class InputSource:
    """Define an input source."""

    def __init__(self, player_id: int, name: str, input_name: str):
        """Init the source."""
        self._player_id = player_id  # type: int
        self._name = name  # type: str
        self._input_name = input_name  # type: str

    def __str__(self):
        """Get a user-readable representation of the source."""
        return "<{} ({})>".format(self._name, self._input_name)

    def __repr__(self):
        """Get a debug representation of the source."""
        return "<{} ({}) on {}>".format(self._name, self._input_name, self._player_id)

    @property
    def name(self) -> str:
        """Get the friendly display name."""
        return self._name

    @property
    def input_name(self) -> str:
        """Get the input source name."""
        return self._input_name

    @property
    def player_id(self) -> int:
        """Get the player id."""
        return self._player_id


class HeosSource:
    """Define an individual heos source."""

    def __init__(self, commands, data: Optional[dict] = None):
        """Init the source class."""
        self._commands = commands
        self._name = None  # type: str
        self._image_url = None  # type: str
        self._type = None  # type: str
        self._source_id = None  # type: int
        self._available = None  # type: bool
        self._service_username = None  # type: str
        self._container = None  # type: bool
        self._container_id = None  # type: str
        self._media_id = None  # type: str
        self._playable = None  # type: bool
        self._index = None  # type: Optional[Dict[str, HeosSource]]
        if data:
            self._from_data(data)

    def _from_data(self, data: dict):
        self._name = data["name"]
        self._image_url = data["image_url"]
        self._type = data["type"]

        source_id = data.get("sid")
        if source_id:
            self._source_id = int(source_id)

        self._available = data.get("available") == "true"
        self._service_username = data.get("service_username")
        self._container = data.get("container") == "yes"
        self._container_id = data.get("cid")
        self._media_id = data.get("mid")
        self._playable = data.get("playable") == "yes"

    def _inherit_ids(self, data: dict):
        if self._source_id is not None and data.get("sid") is None:
            data["sid"] = self._source_id

        if self._container_id is not None and data.get("cid") is None:
            data["cid"] = self._container_id

    def __str__(self):
        """Get a user-readable representation of the source."""
        return "<{} ({})>".format(self._name, self._type)

    def __repr__(self):
        """Get a debug representation of the source."""
        return "<{} ({}) {}>".format(self._name, self._type, self._source_id)

    async def browse(self) -> "Sequence[HeosSource]":
        """Browse the contents of the current source."""
        if self._container:
            raise RuntimeError("Use browse_container instead")

        items = await self._commands.browse(self._source_id)
        sources = []
        for item in items:
            self._inherit_ids(item)
            sources.append(HeosSource(self._commands, item))

        return sources

    async def browse_container(self, start: int, end: int) -> "Sequence[HeosSource]":
        """Browse the contents of the current container."""
        if not self._container:
            raise RuntimeError("Use browse instead")

        items = await self._commands.browse_container(
            self._source_id,
            self._container_id,
            start,
            end,
        )
        sources = []
        for item in items:
            self._inherit_ids(item)
            sources.append(HeosSource(self._commands, item))

        return sources

    async def _build_index(self):
        """Index the child sources belonging to the current source."""
        self._index = {}
        if self._container:
            child_count = 0
            while True:
                child_sources = await self.browse_container(
                    child_count, child_count + const.INDEX_CHUNK_SIZE
                )
                if len(child_sources) == 0:
                    break

                for src in child_sources:
                    self._index[src.name.lower()] = src
                    child_count += 1
        else:
            child_sources = await self.browse()
            for src in child_sources:
                self._index[src.name.lower()] = src

    async def index_all(self) -> int:
        """Recursively index the current container returning the total number of songs.

        Note that this may be slow and memory hungry for large libraries, but subsequent
        calls to get_child_source will be fast.
        """
        song_count = 0
        await self._build_index()
        for src in self._index.values():
            if src.container:
                song_count += await src.index_all()
            else:
                song_count += 1

        return song_count

    async def get_child_source(self, name: str) -> "Optional[HeosSource]":
        """Get the named child source, if it exists."""
        if self._index is None:
            await self._build_index()

        return self._index.get(name.lower())

    @property
    def name(self) -> str:
        """Get the name of the source."""
        return self._name

    @property
    def image_url(self) -> str:
        """Get the image url of the source."""
        return self._image_url

    @property
    def type(self) -> str:
        """Get the type of the source."""
        return self._type

    @property
    def source_id(self) -> int:
        """Get the id of the source."""
        return self._source_id

    @property
    def available(self) -> bool:
        """Return True if the source is available."""
        return self._available

    @property
    def service_username(self) -> str:
        """Get the service username."""
        return self._service_username

    @property
    def media_id(self) -> str:
        """Get the media id."""
        return self._media_id

    @property
    def container(self) -> bool:
        """Return True if the source is a container."""
        return self._container

    @property
    def container_id(self) -> str:
        """Get the ID of the container."""
        return self._container_id

    @property
    def playable(self) -> bool:
        """Return True if the source is playable."""
        return self._playable
