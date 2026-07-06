import hikari

from hikari_components.context import ViewContext

from .components import Button, CallbackT
from .view import View


class MenuScreen(View):
    def __init__(self, parent: "MainMenu"):
        super().__init__()
        self.parent: "MainMenu" = parent

    def add_component(self, component):
        self.components.append(component)

    def render(self):
        return self.components

    def back_button(
        self,
        emoji: hikari.UndefinedOr[hikari.Emoji] = hikari.UNDEFINED,
        style: hikari.ButtonStyle = hikari.ButtonStyle.SECONDARY,
        custom_callback: CallbackT | None = None,
        is_disabled: bool = False,
    ) -> Button | None:
        return (
            Button(
                emoji=emoji,
                style=style,
                callback=custom_callback or self._back_button_callback,
                is_disabled=is_disabled,
            )
            if len(self.parent.screens) >= 1
            else None
        )

    async def _back_button_callback(self, ctx: ViewContext, button: Button) -> None:
        if not self.parent or not self.parent.screens:
            return

        self.parent.screens.pop()
        await ctx.edit_response(components=self.parent.components)


class MainMenu(View):
    def __init__(self):
        super().__init__()

        self.screens: list[MenuScreen] = []

    @property
    def components(self) -> list:
        if not self.screens:
            return []

        return self.screens[-1].components

    @components.setter
    def components(self, value: list):
        """We don't allow setting as to not mess up any of the screen functionality"""
        return

    def add_screen(self, screen: MenuScreen):
        """Adds a new screen to the menu."""
        screen.parent = self
        self.screens.append(screen)

    def remove_screen(self, screen: MenuScreen):
        if screen in self.screens:
            self.screens.remove(screen)

    def replace_screen(self, screen: MenuScreen):
        """Replaces the current screen with a new one."""
        if self.screens:
            self.screens[-1] = screen
            self.screens[-1].parent = self
        else:
            self.add_screen(screen)

    async def push_screen(self, screen: MenuScreen) -> None:
        """Adds a new screen to the menu and immediately update the message."""
        self.add_screen(screen)
        await self.initial_context.edit_initial_response(components=self.components)
