from __future__ import annotations

import asyncio
import traceback
import typing as t

import hikari

from .context import ModalContext, ViewContext

if t.TYPE_CHECKING:
    from .modal import Modal
    from .view import View


class ComponentHandler:
    """A handler that processes component and modal interactions."""

    def __init__(self, bot: hikari.GatewayBotAware, client: t.Any = None):
        self._app = bot
        self._client = client
        self._views: t.Dict[int, View] = {}
        self._modals: t.Dict[str, Modal] = {}
        self._event_manager = self._app.event_manager
        self._event_manager.subscribe(
            hikari.InteractionCreateEvent, self.on_interaction_create
        )
        self._event_manager.subscribe(hikari.StoppingEvent, self.on_shutdown)

    @property
    def views(self) -> t.Dict[int, View]:
        """Returns the current tracked views."""
        return self._views

    async def _find_view(
        self, interaction: hikari.ComponentInteraction
    ) -> t.Optional[View]:
        return self._views.get(interaction.message.id)

    async def on_interaction_create(self, event: hikari.InteractionCreateEvent) -> None:
        if isinstance(event.interaction, hikari.ModalInteraction):
            modal = self._modals.get(event.interaction.custom_id)
            if not modal:
                return

            context = ModalContext(event.interaction)

            values = {}
            for top_comp in event.interaction.components:
                if top_comp.type == hikari.ComponentType.ACTION_ROW:
                    for comp in top_comp.components:
                        values[comp.custom_id] = getattr(
                            comp, "values", getattr(comp, "value", None)
                        )
                elif top_comp.type == hikari.ComponentType.LABEL:
                    comp = top_comp.component
                    values[comp.custom_id] = getattr(
                        comp, "values", getattr(comp, "value", None)
                    )
                else:
                    values[top_comp.custom_id] = getattr(
                        top_comp, "values", getattr(top_comp, "value", None)
                    )

            modal.values = values

            try:
                await modal.callback(context)
            except Exception as e:
                await modal.on_error(context, e)
            finally:
                modal.stop(context)
                self._modals.pop(event.interaction.custom_id, None)
            return

        if not isinstance(event.interaction, hikari.ComponentInteraction):
            return

        view = await self._find_view(event.interaction)
        if not view:
            return

        context = ViewContext(view, self, event.interaction)
        interaction = event.interaction
        button = view.get_from_id(interaction.custom_id)
        if not button:
            return

        context._component = button

        # Auto-sync state for components like SelectMenu
        if hasattr(interaction, "values") and hasattr(button, "values"):
            setattr(button, "values", interaction.values)

        await self.handling_logic(view, interaction, context, button)

    def _remove_handler(self, message_id: int) -> None:
        """Remove a handler from this client."""
        self._views.pop(message_id, None)

    async def on_error(
        self, context: ViewContext, error: Exception
    ) -> None:
        """Called when an error occurs during interaction processing.
        Override this to implement custom error handling.
        """
        traceback.print_exception(type(error), error, error.__traceback__)

    async def send_view(
        self, ctx: t.Any, view: View, flags: t.Optional[hikari.MessageFlag] = None
    ) -> hikari.Message:
        """Helper to send a view using an arc.GatewayContext or similar."""
        if not flags and view.message_flag:
            flags = view.message_flag

        components = view.build()

        if flags:
            msg = await ctx.respond(components=components, flags=flags)
        else:
            msg = await ctx.respond(components=components)

        view.message = await msg.retrieve_message()
        if hasattr(ctx, "command"):
            view.command = ctx.command
        view.initial_context = ctx
        view._client = self

        if hasattr(ctx, "author"):
            view.author = ctx.author
        if hasattr(ctx, "member"):
            view.member = ctx.member

        if not view.has_interactive_components:
            return view.message

        self._views[view.message.id] = view
        await view.schedule_timeout()
        return view.message

    async def handle_timeout(self, view: View) -> None:
        await asyncio.sleep(view.timeout)

        try:
            await view.on_timeout()
        except Exception as e:
            if not isinstance(e, hikari.ForbiddenError):
                print(f"Error during view shutdown: {e}")
        self._views.pop(view.message.id, None)

    async def on_shutdown(self, event: hikari.StoppingEvent) -> None:
        """Called when the bot is shutting down."""

        async def disable_view(view: View):
            try:
                view.disable_all_items()
                if view.message:
                    try:
                        await view.message.edit(components=view.build())
                    except (hikari.NotFoundError, hikari.ForbiddenError):
                        pass
                await view.on_timeout()
            except Exception as e:
                if not isinstance(e, hikari.ForbiddenError):
                    print(f"Error during view shutdown: {e}")

        tasks = [disable_view(view) for view in self._views.values()]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self._views.clear()

    async def send_modal(self, context: t.Any, modal: Modal) -> None:
        """Sends a modal and registers it to listen for interaction."""
        title, custom_id, components = modal.build()
        self._modals[custom_id] = modal

        if hasattr(context, "author"):
            modal.author = context.author
        if hasattr(context, "member"):
            modal.member = context.member

        if hasattr(context, "interaction") and hasattr(
            context.interaction, "create_modal_response"
        ):
            await context.interaction.create_modal_response(
                title, custom_id, components=components
            )
            if hasattr(context, "_issued_response"):
                context._issued_response = True
        elif hasattr(context, "create_modal_response"):
            await context.create_modal_response(title, custom_id, components=components)
            if hasattr(context, "_issued_response"):
                context._issued_response = True
        else:
            raise ValueError(
                f"Context type {type(context)} not supported for send_modal"
            )

    async def handling_logic(
        self,
        view: View,
        interaction: hikari.ComponentInteraction,
        context: ViewContext,
        button: t.Any,
    ) -> None:
        async def auto_defer():
            await asyncio.sleep(1.5)
            await context._safe_defer()

        defer_task = asyncio.create_task(auto_defer())

        async def wrapped_dispatch():
            try:
                await view.dispatch(interaction.custom_id, context, button)
            except asyncio.CancelledError:
                pass
            except Exception as e:
                if not (
                    isinstance(e, hikari.NotFoundError)
                    and "Unknown interaction" in str(e)
                ):
                    await self.on_error(context, e)
            finally:
                defer_task.cancel()
                await context._safe_defer()

        asyncio.create_task(wrapped_dispatch())

    async def purge_views(self) -> None:
        """Purge views from handler that should have expired."""
        for view in list(self._views.values()):
            if view._timeout_task and view._timeout_task.done():
                if view.message and view.message.id in self._views:
                    self._views.pop(view.message.id, None)
