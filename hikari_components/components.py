from __future__ import annotations

import secrets
import typing as t
from collections.abc import Sequence

import hikari
from hikari.api import special_endpoints
from hikari.internal import data_binding, typing_extensions

if t.TYPE_CHECKING:
    from hikari_components.context import ViewContext

CallbackT = t.Callable[["ViewContext", t.Any], t.Coroutine[t.Any, t.Any, None]]

""" General/Message Components """


class Container(hikari.impl.ContainerComponentBuilder):
    def __init__(
        self,
        components: list[t.Any],
        accent_color: hikari.UndefinedOr[hikari.Colour] = hikari.UNDEFINED,
        spoiler: bool = False,
    ):
        super().__init__(
            components=components, accent_color=accent_color, spoiler=spoiler
        )

    @property
    def components(self) -> list:
        """Get the components of the container."""
        self._components = [i for i in self._components if i is not None]
        return self._components

    @components.setter
    def components(self, value: list) -> None:
        """Set the components of the container."""
        self._components = value

    @property
    def spoiler(self) -> bool:
        """Check if the container is a spoiler."""
        return self._spoiler

    @spoiler.setter
    def spoiler(self, value: bool) -> None:
        """Set the spoiler state of the container."""
        self._spoiler = value

    @property
    def accent_color(self) -> hikari.UndefinedOr[hikari.Color]:
        """Get the accent color of the container."""
        return self._accent_color

    @accent_color.setter
    def accent_color(
        self, value: hikari.UndefinedOr[hikari.Color] = hikari.UNDEFINED
    ) -> None:
        """Set the accent color of the container."""
        self._accent_color = value

    def __getitem__(self, item):
        """Get a component by its index."""
        return self._components[item]


class Text(hikari.impl.TextDisplayComponentBuilder):
    def __init__(self, content: str, item_id: str | None = None):
        super().__init__(content=content)
        self.item_id = item_id

    @property
    def content(self) -> str:
        """Get the content of the text component."""
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        """Set the content of the text component."""
        self._content = value


class Row(hikari.impl.MessageActionRowBuilder):
    def __init__(
        self, components: Sequence[special_endpoints.MessageActionRowBuilderComponentsT]
    ):
        super().__init__(components=[i for i in components if i])

    @property
    def components(
        self,
    ) -> Sequence[special_endpoints.MessageActionRowBuilderComponentsT]:
        """Get the components of the row."""
        self._components = [i for i in self._components if i is not None]
        return self._components

    @components.setter
    def components(
        self, value: list[special_endpoints.MessageActionRowBuilderComponentsT]
    ) -> None:
        """Set the components of the row."""
        self._components = value

    def append(
        self, component: special_endpoints.MessageActionRowBuilderComponentsT
    ) -> "Row":
        """Append a component to the row."""
        if component is not None:
            self._components.append(component)
        else:
            raise ValueError("Component cannot be None")
        return self

    def __getitem__(self, item):
        """Get a component by its index."""
        return self._components[item]


class Button(hikari.impl.InteractiveButtonBuilder):
    def __init__(
        self,
        label: str | hikari.UndefinedType = hikari.UNDEFINED,
        *,
        emoji: hikari.Snowflakeish
        | hikari.Emoji
        | str
        | hikari.UndefinedType = hikari.UNDEFINED,
        is_disabled: bool = False,
        style: hikari.ButtonStyle = hikari.ButtonStyle.PRIMARY,
        custom_id: str | None = None,
        callback: CallbackT | None = None,
        item_id: str | None = None,
    ):
        if not custom_id:
            custom_id = secrets.token_hex(16)

        super().__init__(
            custom_id=custom_id,
            style=style,
            label=label,
            emoji=emoji,
            is_disabled=is_disabled,
        )

        self.callback = callback
        self.item_id = item_id

    @property
    def disabled(self) -> bool:
        """Indicates whether the item is disabled or not."""
        return self._is_disabled

    @disabled.setter
    def disabled(self, value: bool) -> None:
        """Set the disabled state of the item."""
        self._is_disabled = value

    @property
    def style(self) -> int | hikari.ButtonStyle:
        """Get the style of the button."""
        return self._style

    @style.setter
    def style(self, value: int | hikari.ButtonStyle) -> None:
        """Set the style of the button."""
        if isinstance(value, int):
            value = hikari.ButtonStyle(value)
        self._style = value

    @property
    def label(self) -> str | hikari.UndefinedOr:
        """Get the label of the button."""
        return self._label

    @label.setter
    def label(self, value: str | hikari.UndefinedOr) -> None:
        """Set the label of the button."""
        self._label = value


class LinkButton(hikari.impl.LinkButtonBuilder):
    def __init__(
        self,
        url: str,
        label: str | hikari.UndefinedType = hikari.UNDEFINED,
        *,
        emoji: hikari.Snowflakeish
        | hikari.Emoji
        | str
        | hikari.UndefinedType = hikari.UNDEFINED,
        is_disabled: bool = False,
        item_id: str | None = None,
    ):
        super().__init__(
            url=url,
            label=label,
            emoji=emoji,
            is_disabled=is_disabled,
        )

        self.item_id = item_id

    @property
    def disabled(self) -> bool:
        """Indicates whether the item is disabled or not."""
        return self._is_disabled

    @disabled.setter
    def disabled(self, value: bool) -> None:
        """Set the disabled state of the item."""
        self._is_disabled = value

    @property
    def label(self) -> str | hikari.UndefinedOr:
        """Get the label of the button."""
        return self._label

    @label.setter
    def label(self, value: str | hikari.UndefinedOr) -> None:
        """Set the label of the button."""
        self._label = value


class Section(hikari.impl.SectionComponentBuilder):
    def __init__(
        self,
        accessory: special_endpoints.SectionBuilderAccessoriesT,
        components: list[special_endpoints.SectionBuilderComponentsT | None],
    ):
        super().__init__(accessory=accessory, components=[i for i in components if i])

    @property
    def accessory(self) -> special_endpoints.SectionBuilderAccessoriesT:
        """Get the accessory of the section."""
        return self._accessory

    @accessory.setter
    def accessory(self, value: special_endpoints.SectionBuilderAccessoriesT) -> None:
        """Set the accessory of the section."""
        self._accessory = value

    @property
    def components(self) -> Sequence[special_endpoints.SectionBuilderComponentsT]:
        """Get the components of the container."""
        self._components = [i for i in self._components if i is not None]
        return self._components

    @components.setter
    def components(
        self, value: list[special_endpoints.SectionBuilderComponentsT]
    ) -> None:
        """Set the components of the container."""
        self._components = value

    def __getitem__(self, item):
        """Get a component by its index."""
        return self._components[item]


class Thumbnail(hikari.impl.ThumbnailComponentBuilder):
    def __init__(
        self,
        media: hikari.Resourceish,
        *,
        description: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        spoiler: bool = False,
    ):
        super().__init__(media=media, description=description, spoiler=spoiler)

    @property
    def media(self) -> hikari.Resourceish:
        """Get the media of the thumbnail."""
        return self._media

    @media.setter
    def media(self, value: hikari.Resourceish) -> None:
        """Set the media of the thumbnail."""
        self._media = value

    @property
    def description(self) -> hikari.UndefinedOr[str]:
        """Get the description of the thumbnail."""
        return self._description

    @description.setter
    def description(self, value: hikari.UndefinedOr[str]) -> None:
        """Set the description of the thumbnail."""
        self._description = value

    @property
    def spoiler(self) -> bool:
        """Check if the thumbnail is a spoiler."""
        return self._spoiler

    @spoiler.setter
    def spoiler(self, value: bool) -> None:
        """Set the spoiler state of the thumbnail."""
        self._spoiler = value

    @typing_extensions.override
    def build(
        self,
    ) -> tuple[
        t.MutableMapping[str, t.Any],
        t.Sequence[hikari.files.Resource[hikari.files.AsyncReader]],
    ]:
        media_resource = hikari.files.ensure_resource(self._media)

        payload = data_binding.JSONObjectBuilder()
        payload["type"] = self.type
        payload["media"] = {"url": media_resource.url}
        payload["spoiler"] = self._spoiler

        payload.put("id", self._id)
        payload.put("description", self._description)

        if "attachment://" in media_resource.url:
            return payload, (media_resource,)
        return payload, ()


class MediaGallery(hikari.impl.MediaGalleryComponentBuilder):
    def __init__(self, items: Sequence[special_endpoints.MediaGalleryItemBuilder]):
        super().__init__(items=[i for i in items if i.media])

    @property
    def items(self) -> Sequence[special_endpoints.MediaGalleryItemBuilder]:
        """Get the items of the media gallery."""
        return self._items

    @items.setter
    def items(self, value: list[special_endpoints.MediaGalleryItemBuilder]) -> None:
        """Set the items of the media gallery."""
        self._items = value

    @typing_extensions.override
    def build(
        self,
    ) -> tuple[
        t.MutableMapping[str, t.Any],
        Sequence[hikari.files.Resource[hikari.files.AsyncReader]],
    ]:
        items_payload: Sequence[t.MutableMapping[str, t.Any]] = []
        attachments: Sequence[hikari.files.Resource[hikari.files.AsyncReader]] = []
        for item in self.items:
            item_payload, item_attachments = item.build()
            items_payload.append(item_payload)
            attachments.extend(
                tuple(
                    [i for i in item_attachments if i.url.startswith("attachment://")]
                )
            )

        payload = data_binding.JSONObjectBuilder()
        payload["type"] = self.type
        payload["items"] = items_payload
        payload.put("id", self._id)
        return payload, attachments


class MediaImage(hikari.impl.MediaGalleryItemBuilder):
    def __init__(
        self,
        media: hikari.files.Resourceish,
        description: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        spoiler: bool = False,
    ):
        super().__init__(media=media, description=description, spoiler=spoiler)

    @property
    def media(self) -> hikari.files.Resourceish:
        """Get the media of the gallery item."""
        return self._media

    @media.setter
    def media(self, value: hikari.files.Resourceish) -> None:
        """Set the media of the gallery item."""
        self._media = value

    @property
    def is_spoiler(self) -> bool:
        """Check if the gallery item is a spoiler."""
        return self._spoiler

    @is_spoiler.setter
    def is_spoiler(self, value: bool) -> None:
        """Set the spoiler state of the gallery item."""
        self._spoiler = value

    @typing_extensions.override
    def build(
        self,
    ) -> tuple[
        t.MutableMapping[str, t.Any],
        t.Sequence[hikari.files.Resource[hikari.files.AsyncReader]],
    ]:
        media_resource = hikari.files.ensure_resource(self._media)

        payload = data_binding.JSONObjectBuilder()
        payload["media"] = {"url": media_resource.url}
        payload["spoiler"] = self._spoiler
        payload.put("description", self._description)

        if "attachment://" in media_resource.url:
            return payload, (media_resource,)
        return payload, ()


class File(hikari.impl.FileComponentBuilder):
    def __init__(self, file: hikari.files.Resourceish, is_spoiler: bool = False):
        super().__init__(file=file, spoiler=is_spoiler)

    @property
    def file(self) -> hikari.Resourceish:
        """Get the file path of the component."""
        return self._file

    @file.setter
    def file(self, value: hikari.Resourceish) -> None:
        """Set the file path of the component."""
        self._file = value

    @property
    def is_spoiler(self) -> bool:
        """Check if the gallery item is a spoiler."""
        return self._spoiler

    @is_spoiler.setter
    def is_spoiler(self, value: bool) -> None:
        """Set the spoiler state of the gallery item."""
        self._spoiler = value

    @typing_extensions.override
    def build(
        self,
    ) -> tuple[
        t.MutableMapping[str, t.Any],
        t.Sequence[hikari.files.Resource[hikari.files.AsyncReader]],
    ]:
        file_resource = hikari.files.ensure_resource(self._file)

        payload = data_binding.JSONObjectBuilder()
        payload["type"] = self.type
        payload["spoiler"] = self._spoiler
        payload["file"] = {"url": file_resource.url}
        payload.put("id", self._id)

        if "attachment://" in file_resource.url:
            return payload, (file_resource,)
        return payload, ()


class Separator(hikari.impl.SeparatorComponentBuilder):
    def __init__(
        self,
        divider: bool = False,
        spacing: hikari.SpacingType = hikari.SpacingType.SMALL,
    ):
        super().__init__(divider=divider, spacing=spacing)

    @property
    def divider(self) -> bool | hikari.UndefinedType:
        """Check if the separator is a divider."""
        return self._divider

    @divider.setter
    def divider(self, value: bool) -> None:
        """Set the divider state of the separator."""
        self._divider = value

    @property
    def spacing(self) -> hikari.UndefinedOr[hikari.SpacingType]:
        """Get the spacing type of the separator."""
        return self._spacing

    @spacing.setter
    def spacing(self, value: hikari.SpacingType) -> None:
        """Set the spacing type of the separator."""
        self._spacing = value


class SelectOption(hikari.impl.SelectOptionBuilder):
    def __init__(
        self,
        label: str,
        value: str | None = None,
        description: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        emoji: hikari.UndefinedOr[hikari.Emoji | str | int | None] = hikari.UNDEFINED,
        is_default: bool = False,
        search_query: str | None = None,
    ):
        if not value:
            value = secrets.token_hex(16)
        if emoji is None:
            emoji = hikari.UNDEFINED

        super().__init__(
            label=label,
            value=value,
            description=description,
            emoji=emoji,
            is_default=is_default,
        )
        if search_query is not None:
            self.search_query = search_query

    @property
    def label(self) -> str:
        """Get the label of the select option."""
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        """Set the label of the select option."""
        self._label = value

    @property
    def value(self) -> str:
        """Get the value of the select option."""
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        """Set the value of the select option."""
        self._value = value

    @property
    def description(self) -> hikari.UndefinedOr[str]:
        """Get the description of the select option."""
        return self._description

    @description.setter
    def description(self, value: hikari.UndefinedOr[str] = hikari.UNDEFINED) -> None:
        """Set the description of the select option."""
        self._description = value

    @property
    def emoji(self) -> hikari.Emoji | str | hikari.UndefinedType | hikari.Snowflakeish:
        """Get the emoji of the select option."""
        return self._emoji

    @emoji.setter
    def emoji(
        self,
        value: hikari.Emoji
        | str
        | hikari.UndefinedType
        | hikari.Snowflakeish = hikari.UNDEFINED,
    ) -> None:
        """Set the emoji of the select option."""
        self._emoji = value

    @property
    def is_default(self) -> bool:
        """Check if the select option is default."""
        return self._is_default

    @is_default.setter
    def is_default(self, value: bool) -> None:
        """Set the default state of the select option."""
        self._is_default = value


class TextSelectMenu(hikari.impl.TextSelectMenuBuilder):
    def __init__(
        self,
        *,
        options: Sequence[SelectOption],
        callback: CallbackT | None = None,
        placeholder: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        min_values: int = 0,
        max_values: int = 1,
        is_disabled: bool = False,
        is_required: bool = False,
        custom_id: str | None = None,
        item_id: str | None = None,
    ):
        if not custom_id:
            custom_id = secrets.token_hex(16)
        super().__init__(
            custom_id=custom_id,
            options=options,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            is_disabled=is_disabled,
            is_required=is_required,
        )
        self.callback = callback
        self.item_id = item_id

    @property
    def options(self) -> Sequence[special_endpoints.SelectOptionBuilder]:
        """Get the options of the select menu."""
        return self._options

    @options.setter
    def options(self, value: list[special_endpoints.SelectOptionBuilder]) -> None:
        """Set the options of the select menu."""
        self._options = value

    @property
    def placeholder(self) -> hikari.UndefinedOr[str]:
        """Get the placeholder text of the select menu."""
        return self._placeholder

    @placeholder.setter
    def placeholder(self, value: hikari.UndefinedOr[str] = hikari.UNDEFINED) -> None:
        """Set the placeholder text of the select menu."""
        self._placeholder = value

    @property
    def min_values(self) -> int:
        """Get the minimum number of values that can be selected."""
        return self._min_values

    @min_values.setter
    def min_values(self, value: int) -> None:
        """Set the minimum number of values that can be selected."""
        self._min_values = value

    @property
    def max_values(self) -> int:
        """Get the maximum number of values that can be selected."""
        return self._max_values

    @max_values.setter
    def max_values(self, value: int) -> None:
        """Set the maximum number of values that can be selected."""
        self._max_values = value

    @property
    def disabled(self) -> bool:
        """Check if the select menu is disabled."""
        return self._is_disabled

    @disabled.setter
    def disabled(self, value: bool) -> None:
        """Set the disabled state of the select menu."""
        self._is_disabled = value


class TextSelectMenuRow(Row):
    """Text Select Menu already wrapped in a Row component for message components"""

    def __init__(
        self,
        *,
        options: Sequence[SelectOption],
        callback: CallbackT | None = None,
        placeholder: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        min_values: int = 0,
        max_values: int = 1,
        is_disabled: bool = False,
        custom_id: str | None = None,
        item_id: str | None = None,
    ):
        self._menu = TextSelectMenu(
            custom_id=custom_id,
            callback=callback,
            options=options,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            is_disabled=is_disabled,
            item_id=item_id,
        )
        super().__init__([self._menu])

    def __getattr__(self, name: str):
        """Forward any missing attribute reads to the underlying SelectMenu."""
        return getattr(self._menu, name)

    def __setattr__(self, name: str, value: t.Any):
        """Forward attribute writes to the SelectMenu, unless it belongs to the Row itself."""
        if name in ("_menu", "components", "_components") or name.startswith("__"):
            super().__setattr__(name, value)
        elif hasattr(TextSelectMenuRow, name) or hasattr(self._menu, name):
            setattr(self._menu, name, value)
        else:
            super().__setattr__(name, value)


class SelectMenu(hikari.impl.SelectMenuBuilder):
    def __init__(
        self,
        *,
        type: hikari.ComponentType,
        callback: CallbackT | None = None,
        placeholder: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        min_values: int = 0,
        max_values: int = 1,
        is_disabled: bool = False,
        is_required: bool = False,
        custom_id: str | None = None,
        item_id: str | None = None,
    ):
        if not custom_id:
            custom_id = secrets.token_hex(16)
        super().__init__(
            custom_id=custom_id,
            type=type,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            is_disabled=is_disabled,
            is_required=is_required,
        )
        self.callback = callback
        self.item_id = item_id

    @property
    def placeholder(self) -> hikari.UndefinedOr[str]:
        """Get the placeholder text of the select menu."""
        return self._placeholder

    @placeholder.setter
    def placeholder(self, value: hikari.UndefinedOr[str] = hikari.UNDEFINED) -> None:
        """Set the placeholder text of the select menu."""
        self._placeholder = value

    @property
    def min_values(self) -> int:
        """Get the minimum number of values that can be selected."""
        return self._min_values

    @min_values.setter
    def min_values(self, value: int) -> None:
        """Set the minimum number of values that can be selected."""
        self._min_values = value

    @property
    def max_values(self) -> int:
        """Get the maximum number of values that can be selected."""
        return self._max_values

    @max_values.setter
    def max_values(self, value: int) -> None:
        """Set the maximum number of values that can be selected."""
        self._max_values = value

    @property
    def disabled(self) -> bool:
        """Check if the select menu is disabled."""
        return self._is_disabled

    @disabled.setter
    def disabled(self, value: bool) -> None:
        """Set the disabled state of the select menu."""
        self._is_disabled = value


class SelectMenuRow(Row):
    """Select Menu already wrapped in a Row component for message components"""

    def __init__(
        self,
        *,
        type: hikari.ComponentType,
        callback: CallbackT | None = None,
        placeholder: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        min_values: int = 0,
        max_values: int = 1,
        is_disabled: bool = False,
        is_required: bool = False,
        custom_id: str | None = None,
        item_id: str | None = None,
    ):
        self._menu = SelectMenu(
            custom_id=custom_id,
            callback=callback,
            type=type,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            is_disabled=is_disabled,
            item_id=item_id,
            is_required=is_required,
        )
        super().__init__([self._menu])

    def __getattr__(self, name: str):
        """Forward any missing attribute reads to the underlying SelectMenu."""
        return getattr(self._menu, name)

    def __setattr__(self, name: str, value: t.Any):
        """Forward attribute writes to the SelectMenu, unless it belongs to the Row itself."""
        if name in ("_menu", "components", "_components") or name.startswith("__"):
            super().__setattr__(name, value)
        elif hasattr(SelectMenu, name) or hasattr(self._menu, name):
            setattr(self._menu, name, value)
        else:
            super().__setattr__(name, value)


""" Modal Components """


class ModalLabel(hikari.impl.LabelComponentBuilder):
    def __init__(
        self, label: str, component: t.Any, description: hikari.UndefinedOr[str] = hikari.UNDEFINED
    ):
        super().__init__(label=label, description=description, component=component)


class TextInput(hikari.impl.TextInputBuilder):
    def __init__(
        self,
        *,
        custom_id: str,
        label: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        style: hikari.TextInputStyle = hikari.TextInputStyle.SHORT,
        placeholder: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        value: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        required: bool = True,
        min_length: int = 0,
        max_length: int = 4000,
    ):
        super().__init__(
            custom_id=custom_id,
            label=label,
            style=style,
            placeholder=placeholder,
            value=value,
            required=required,
            min_length=min_length,
            max_length=max_length,
        )


class ModalTextInput(ModalLabel):
    def __init__(
        self,
        label: str,
        custom_id: str,
        description: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        text: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        style: hikari.TextInputStyle = hikari.TextInputStyle.SHORT,
        placeholder: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        value: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        required: bool = True,
        min_length: int = 0,
        max_length: int = 4000,
    ):
        super().__init__(
            label=label,
            description=description,
            component=TextInput(
                custom_id=custom_id,
                label=text,
                style=style,
                placeholder=placeholder,
                value=value,
                required=required,
                min_length=min_length,
                max_length=max_length,
            ),
        )


class FileUploadComponent(hikari.impl.FileUploadComponentBuilder):
    def __init__(
        self,
        custom_id: str,
        min_values: int = 1,
        max_values: int = 1,
        is_required: bool = True,
    ):
        super().__init__(
            custom_id=custom_id,
            min_values=min_values,
            max_values=max_values,
            is_required=is_required,
        )


class ModalFileUpload(ModalLabel):
    """File Upload Component already wrapped in a LabelComponentBuilder"""

    def __init__(
        self,
        label: str,
        custom_id: str,
        description: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        min_values: int = 1,
        max_values: int = 1,
        is_required: bool = True,
    ):
        self._menu = FileUploadComponent(
            custom_id=custom_id,
            min_values=min_values,
            max_values=max_values,
            is_required=is_required,
        )
        super().__init__(label=label, description=description, component=self._menu)


class ModalSelectMenu(ModalLabel):
    def __init__(
        self,
        *,
        label: str,
        custom_id: str,
        description: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        type: hikari.ComponentType,
        placeholder: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        min_values: int = 0,
        max_values: int = 1,
        is_disabled: bool = False,
        is_required: bool = False,
        item_id: str | None = None,
    ):
        self._menu = SelectMenu(
            custom_id=custom_id,
            callback=None,
            type=type,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            is_disabled=is_disabled,
            item_id=item_id,
            is_required=is_required,
        )
        super().__init__(label=label, description=description, component=self._menu)


class ModalTextSelectMenu(ModalLabel):
    def __init__(
        self,
        *,
        label: str,
        custom_id: str,
        description: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        options: Sequence[SelectOption],
        placeholder: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        min_values: int = 0,
        max_values: int = 1,
        is_disabled: bool = False,
        is_required: bool = False,
        item_id: str | None = None,
    ):
        self._menu = TextSelectMenu(
            custom_id=custom_id,
            callback=None,
            options=options,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            is_disabled=is_disabled,
            item_id=item_id,
            is_required=is_required,
        )
        super().__init__(label=label, description=description, component=self._menu)
