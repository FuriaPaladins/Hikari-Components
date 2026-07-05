from __future__ import annotations

import asyncio
import typing as t

import hikari

if t.TYPE_CHECKING:
    from .context import ViewContext
    from .handler import ComponentHandler


class View:
    """Base View class for managing state and components."""

    def __init__(self, timeout: float = 120.0) -> None:
        self.components: list[t.Any] = []
        self.timeout = timeout
        self.message: t.Optional[hikari.Message] = None
        self.initial_context: t.Any = None
        self.command: t.Any = None

        self.custom_id_map: t.Dict[str, t.Any] = {}
        self.item_id_map: t.Dict[str, t.Any] = {}
        self._client: t.Optional["ComponentHandler"] = None
        self._timeout_task: t.Optional[asyncio.Task[None]] = None
        self._wait_future: t.Optional[asyncio.Future[None]] = None
        self.message_flag: t.Optional[hikari.MessageFlag] = None

        self.author: t.Optional[hikari.User] = None
        self.member: t.Optional[hikari.InteractionMember] = None

    @property
    def has_interactive_components(self) -> bool:
        """Returns True if there is at least one component with a custom_id."""
        return any(
            hasattr(item, "custom_id") and item.custom_id
            for item in self._walk_components()
        )

    def _find_component_by_attr(
        self, attr_name: str, attr_value: str
    ) -> t.Optional[t.Any]:
        """Recursively traverses to find a component by a specific attribute."""

        def traverse(component: t.Any) -> t.Optional[t.Any]:
            if getattr(component, attr_name, None) == attr_value:
                return component

            for child in getattr(component, "components", []):
                if found := traverse(child):
                    return found

            if accessory := getattr(component, "accessory", None):
                if found := traverse(accessory):
                    return found

            return None

        for comp in self.components:
            if found := traverse(comp):
                return found

        return None

    def get_item(self, item_id: str) -> t.Optional[t.Any]:
        """Gets an interactive component dynamically by its item ID."""
        return self._find_component_by_attr("item_id", item_id)

    def get_from_id(self, custom_id: str) -> t.Optional[t.Any]:
        """Gets an interactive component dynamically by its custom ID."""
        return self._find_component_by_attr("custom_id", custom_id)

    async def view_check(self, context: "ViewContext") -> bool:
        """Called before a component callback is executed.
        If this returns False, the callback is not executed and on_check_failure is called.
        """
        return True

    async def on_check_failure(self, context: "ViewContext") -> None:
        """Called when view_check returns False.
        Defaults to sending an ephemeral unauthorized message.
        """
        await context.respond(
            "You are not authorized to interact with this!",
            flags=hikari.MessageFlag.EPHEMERAL,
        )

    async def on_timeout(self) -> None:
        """Called when the view times out. Disables all items by default."""
        self.disable_all_items()
        if self.message:
            try:
                components = self.build()
                if self.initial_context and hasattr(
                    self.initial_context, "edit_response"
                ):
                    await self.initial_context.edit_response(components=components)
                elif self.initial_context and hasattr(
                    self.initial_context, "interaction"
                ):
                    await self.initial_context.interaction.edit_initial_response(
                        components=components
                    )
                else:
                    await self.message.edit(components=components)
            except Exception:
                pass
        if self._wait_future and not self._wait_future.done():
            self._wait_future.set_result(None)

    async def schedule_timeout(self) -> None:
        """Schedules the view timeout."""
        if self._timeout_task and not self._timeout_task.done():
            self._timeout_task.cancel()

        if self.timeout is not None and self.timeout > 0:
            if self._client:
                self._timeout_task = asyncio.create_task(
                    self._client.handle_timeout(self)
                )

    def stop(self) -> None:
        """Stops listening for interactions and removes from handler."""
        if self._timeout_task and not self._timeout_task.done():
            self._timeout_task.cancel()
        if self._client and self.message:
            self._client.views.pop(self.message.id, None)

        if self._wait_future and not self._wait_future.done():
            self._wait_future.set_result(None)

    async def wait(self, timeout: t.Optional[float] = None) -> None:
        """Waits for the view to stop or timeout.
        Raises asyncio.TimeoutError if the specified timeout is exceeded before the view finishes.
        """
        if not self._wait_future:
            self._wait_future = asyncio.get_running_loop().create_future()

        await asyncio.wait_for(self._wait_future, timeout=timeout)

    def _walk_components(self) -> t.Iterator[t.Any]:
        """Recursively yields every component in the view tree."""

        def traverse(component: t.Any) -> t.Iterator[t.Any]:
            yield component

            for child in getattr(component, "components", []):
                yield from traverse(child)

            accessory = getattr(component, "accessory", None)
            if accessory:
                yield from traverse(accessory)

        for comp in self.components:
            yield from traverse(comp)

    def disable_all_items(self) -> None:
        """Disables all interactive components in the view."""
        for item in self._walk_components():
            if hasattr(item, "custom_id") and item.custom_id:
                item.disabled = True

    async def dispatch(
        self, custom_id: str, context: "ViewContext", component: t.Any
    ) -> None:
        """Dispatches an interaction to the correct component callback."""
        passed = await self.view_check(context)
        if not passed:
            await self.on_check_failure(context)
            return

        await self.schedule_timeout()

        if component.callback:
            await component.callback(context, component)

    def build(self) -> t.Sequence[hikari.api.ComponentBuilder]:
        """Builds the raw hikari builders for the components in this view."""
        return self.components
