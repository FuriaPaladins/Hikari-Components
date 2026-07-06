import asyncio
import os
import typing as t

import hikari

from .context import ModalContext


class Modal:
    """A base class for Discord Modals."""

    def __init__(
        self,
        title: str,
        components,
        custom_id: t.Optional[str] = None,
        timeout: float = 120.0,
    ) -> None:
        self.title = title
        self.custom_id = custom_id or os.urandom(16).hex()
        self.timeout = timeout
        self.components: t.List[t.Any] = []
        self._values: t.Dict[str, str] = {}
        self._wait_future: t.Optional[asyncio.Future[t.Optional[ModalContext]]] = None

        self.author: t.Optional[hikari.User] = None
        self.member: t.Optional[hikari.InteractionMember] = None

        self.components = components

    @property
    def values(self) -> t.Dict[str, str]:
        """A dictionary mapping custom_ids to their submitted string values."""
        return self._values

    @values.setter
    def values(self, val: t.Dict[str, str]) -> None:
        self._values = val

    def get_value(self, custom_id: str) -> t.Optional[str]:
        """Gets the submitted value for a specific text input's custom_id."""
        return self._values.get(custom_id)

    def add_item(self, item: t.Any) -> None:
        """Adds a component to the modal."""
        self.components.append(item)

    def build(self) -> t.Tuple[str, str, t.List[hikari.api.ComponentBuilder]]:
        """Builds the modal into a format suitable for hikari."""
        return self.title, self.custom_id, self.components

    async def callback(self, ctx: ModalContext) -> None:
        """Called when the modal is submitted."""
        pass

    async def on_timeout(self) -> None:
        """Called when the modal times out."""
        pass

    async def on_error(self, context: ModalContext, error: Exception) -> None:
        """Called when an error occurs during the callback."""
        print(f"Ignoring unhandled exception in modal {self.__class__.__name__}: {error}")

    def stop(self, context: t.Optional[ModalContext] = None) -> None:
        """Resolves the wait future for this modal."""
        if self._wait_future and not self._wait_future.done():
            self._wait_future.set_result(context)

    async def wait(self, timeout: float = 120.0) -> t.Optional[ModalContext]:
        """Waits for the modal to be submitted or timeout.
        Returns the ModalContext if submitted.
        Raises asyncio.TimeoutError if the timeout is exceeded.
        """
        if not self._wait_future or self._wait_future.done():
            self._wait_future = asyncio.get_running_loop().create_future()

        try:
            return await asyncio.wait_for(
                self._wait_future, timeout=timeout or self.timeout
            )
        except asyncio.TimeoutError:
            self.stop()
            raise
