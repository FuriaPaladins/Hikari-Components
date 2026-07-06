from __future__ import annotations

import asyncio
import datetime
import typing as t

import hikari


if t.TYPE_CHECKING:
    from .handler import ComponentHandler
    from .view import View


class BaseContext:
    """Base context for interactions."""

    def __init__(
        self, interaction: t.Union[hikari.ComponentInteraction, hikari.ModalInteraction]
    ) -> None:
        self._interaction = interaction
        self._issued_response = False
        self._lock = asyncio.Lock()

        self._delete_after_task: t.Optional[asyncio.Task[None]] = None
        
    @property
    def interaction(
        self,
    ) -> t.Union[hikari.ComponentInteraction, hikari.ModalInteraction]:
        """The underlying interaction object."""
        return self._interaction

    @property
    def app(self) -> hikari.RESTAware:
        """The application instance."""
        return self._interaction.app

    @property
    def author(self) -> hikari.User:
        """The user who triggered the interaction."""
        return self._interaction.user

    @property
    def member(self) -> t.Optional[hikari.InteractionMember]:
        """The member who triggered the interaction, if any."""
        return self._interaction.member

    @property
    def user(self) -> hikari.User:
        """The user who triggered this interaction."""
        return self._interaction.user

    @property
    def app_permissions(self) -> hikari.Permissions:
        """The permissions of the bot. Will be None in DMs."""
        return self._interaction.app_permissions

    @property
    def channel_id(self) -> hikari.Snowflake:
        """The ID of the channel the context represents."""
        return self._interaction.channel_id

    @property
    def channel(self) -> hikari.InteractionChannel:
        """The channel the context represents."""
        return self._interaction.channel

    @property
    def guild_id(self) -> hikari.Snowflake | None:
        """The ID of the guild the context represents. Will be None in DMs."""
        return self._interaction.guild_id
        
    async def _safe_defer(self) -> None:
        """Internal auto-deferral mechanism."""
        async with self._lock:
            if self._issued_response:
                return
            try:
                await self._interaction.create_initial_response(
                    hikari.ResponseType.DEFERRED_MESSAGE_UPDATE
                )
                self._issued_response = True
            except (hikari.NotFoundError, hikari.BadRequestError):
                pass

    async def _do_delete_after(self, delay: float) -> None:
            """Internal task to sleep and delete the initial response."""
            await asyncio.sleep(delay)
            try:
                await self._interaction.delete_initial_response()
            except (hikari.NotFoundError, hikari.BadRequestError):
                pass  # Message was already deleted or interaction expired
            finally:
                self._delete_after_task = None
    
    def delete_after(self, delay: t.Union[int, float, datetime.timedelta]) -> None:
            """Delete the response after the specified delay.
    
            Parameters
            ----------
            delay : Union[int, float, datetime.timedelta]
                The delay after which the response should be deleted.
            """
            if self._delete_after_task is not None:
                raise RuntimeError("A delete_after task is already running.")
    
            if isinstance(delay, datetime.timedelta):
                delay = delay.total_seconds()
                
            self._delete_after_task = asyncio.create_task(self._do_delete_after(delay))
                        
    async def respond(self, *args: t.Any, delete_after: t.Optional[t.Union[int, float, datetime.timedelta]] = None, **kwargs: t.Any) -> t.Any:
        """Respond to the interaction.
        This creates an initial response or executes a webhook if already responded.
        """
        async with self._lock:
            if self._issued_response:
                response = await self._interaction.execute(*args, **kwargs)
            else:
                self._issued_response = True
                response = await self._interaction.create_initial_response(
                    hikari.ResponseType.MESSAGE_CREATE, *args, **kwargs
                )
        
        if delete_after is not None:
            self.delete_after(delete_after)
            
        return response

    async def edit_response(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
        """Edit the interaction's initial response."""
        async with self._lock:
            if self._issued_response:
                return await self._interaction.edit_initial_response(*args, **kwargs)

            self._issued_response = True
            try:
                return await self._interaction.create_initial_response(
                    hikari.ResponseType.MESSAGE_UPDATE, *args, **kwargs
                )
            except hikari.NotFoundError:
                return await self._interaction.edit_initial_response(*args, **kwargs)

    async def defer(self, *args: t.Any, **kwargs: t.Any) -> None:
        """Defer the interaction.
        This sends a DEFERRED_MESSAGE_UPDATE response to Discord.
        """
        async with self._lock:
            if not self._issued_response:
                self._issued_response = True
                await self._interaction.create_initial_response(
                    hikari.ResponseType.DEFERRED_MESSAGE_UPDATE, *args, **kwargs
                )


class ViewContext(BaseContext):
    """A context object wrapping a component interaction."""

    __slots__ = ("_view", "_component", "_client")

    def __init__(
        self,
        view: View,
        client: ComponentHandler,
        interaction: hikari.ComponentInteraction,
        component: t.Any = None,
    ) -> None:
        super().__init__(interaction)
        self._view = view
        self._client = client
        self._component = component

    @property
    def interaction(self) -> hikari.ComponentInteraction:
        """The underlying interaction object."""
        return t.cast(hikari.ComponentInteraction, self._interaction)

    @property
    def view(self) -> View:
        """The view this context belongs to."""
        return self._view

    @property
    def component(self) -> t.Any:
        """The component that triggered this interaction."""
        return self._component

    @property
    def client(self) -> ComponentHandler:
        """The client/handler managing this view."""
        return self._client


class ModalContext(BaseContext):
    """Context for a modal interaction."""

    def __init__(self, interaction: hikari.ModalInteraction) -> None:
        super().__init__(interaction)

    @property
    def interaction(self) -> hikari.ModalInteraction:
        """The underlying interaction object."""
        return t.cast(hikari.ModalInteraction, self._interaction)
