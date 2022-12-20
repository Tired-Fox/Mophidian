from __future__ import annotations

from typing import Any, Optional
import inspect

from teddecor import p_value, TED


class TypesDefault:
    """Representation of a values valid types along with it's default value."""

    def __init__(
        self,
        *args: type,
        nested_types: Optional[list] = None,
        default: Any = None,
    ) -> None:
        self.types = tuple(val for val in args if not isinstance(val, (TypesDefault, dict)))
        self.nested_types = nested_types
        if len(self.types) > 0 and default is not None and not isinstance(default, self.types):
            raise TypeError(
                TED.parse(
                    f"*Default value must one of the valid types \
\\[{', '.join(f'[@F #f5a97f]{val.__name__}[@]' for val in self.types)}\\]"
                )
            )

        if len(args) == 0:
            self.types = (type(default),)

        if isinstance(default, dict):
            self.__default = dict(default)
        elif isinstance(default, list):
            self.__default = list(default)
        elif isinstance(default, tuple):
            self.__default = tuple(default)
        else:
            self.__default = default

    @property
    def default(self) -> Any:
        """The default value of the variable."""
        return self.__default

    def __repr__(self) -> str:
        return f"{' | '.join([t.__name__ for t in self.types])} = {repr(self.__default)}"


def path(path: list[str]) -> str:
    return '.'.join(f'[@F #eed49f]{TED.encode(val)}[@F]' for val in path)


def config(obj):
    class Config:  # pylint: disable=too-few-public-methods
        """Base config class. Built from the attributes of another class.
        Similar to dataclass, but with typing and default values."""

        def __init__(self, cfg: Optional[dict] = None):
            self.attributes = []
            self.validated = []
            self.name = obj.__name__.lower()
            self.config = cfg
            for i in inspect.getmembers(obj):
                if not i[0].startswith('_'):
                    if not inspect.ismethod(i[1]):
                        var, value = i
                        if (
                            not isinstance(value, (TypesDefault, list, tuple, dict))
                            and not "config.<locals>.Config" in value.__class__.__qualname__
                        ):
                            raise ValueError(
                                TED.parse(
                                    f"*[@F #eed49f]{TED.encode(str(var))}[@] is not a valid \
[@F #f5a97f]TypesDefault[@F], [@F #f5a97f]list[@F], [@F #f5a97f]tuple[@F], [@F #f5a97f]dict[@F] or \
[@F #f5a97f]Config[@F]"
                                )
                            )
                        setattr(self, var, value)
                        self.attributes.append(var)

            if cfg is not None:
                self.validate()

        def __iter__(self):
            for key in self.attributes:
                if key not in self.validated:
                    yield key, self.__get_default(getattr(self, key))
                else:
                    yield key, getattr(self, key)

        def __get_default(self, value) -> Any:
            if isinstance(value, TypesDefault):
                return value.default
            elif isinstance(value, list):
                return list()
            elif isinstance(value, tuple):
                return tuple()
            elif isinstance(value, dict):
                return value
            elif "config.<locals>.Config" in value.__class__.__qualname__:
                return dict(value)

        def validate(self, cfg: Optional[dict] = None, parent: Optional[list[str]] = None):
            cfg = cfg or self.config or {}
            parent = parent or []
            for key, value in cfg.items():
                if not hasattr(self, key):
                    raise ValueError(
                        TED.parse(
                            f"Invalid variable [@F #eed49f]{key}[@F] in \
{path([*parent, self.name])}"
                        )
                    )

                if isinstance(getattr(self, key), list) and (
                    not isinstance(value, list)
                    or any(type(val) not in getattr(self, key) for val in value)
                ):
                    raise ValueError(
                        TED.parse(
                            f"*{path([*parent, self.name, key])} must be a list with one of these types \
({', '.join(f'[@F #f5a97f]{val.__name__}[@]' for val in getattr(self, key))})"
                        )
                    )

                if isinstance(getattr(self, key), tuple) and (
                    not isinstance(value, tuple) or type(value) not in list(getattr(self, key))
                ):
                    raise ValueError(
                        TED.parse(
                            f"*{path([*parent, self.name, key])} must be a tuple with one of these types \
({', '.join(f'[@F #f5a97f]{val.__name__}[@]' for val in getattr(self, key))})"
                        )
                    )
                
                if isinstance(getattr(self, key), dict) and not isinstance(value, dict):
                    raise ValueError(
                        TED.parse(
                            f"*{path([*parent, self.name, key])} must be a dict"
                        )
                    )

                if isinstance(getattr(self, key), TypesDefault):
                    if type(value) not in getattr(self, key).types:
                        raise ValueError(
                            TED.parse(
                                f"*{path([*parent, self.name, key])} must be one \
of these types ({', '.join(f'[@F #f5a97f]{val.__name__}[@]' for val in getattr(self, key).types)})"
                            )
                        )

                    if (
                        isinstance(value, (list, tuple))
                        and getattr(self, key).nested_types is not None
                        and any(type(val) not in getattr(self, key).nested_types for val in value)
                    ):
                        raise ValueError(
                            TED.parse(
                                f"*Values in {path([*parent, self.name, key])} must be one \
of these types ({', '.join(f'[@F #f5a97f]{val.__name__}[@]' for val in getattr(self, key).nested_types)})"
                            )
                        )

                if "config.<locals>.Config" in getattr(self, key).__class__.__qualname__:
                    getattr(self, key).validate(value, [*parent, self.name])
                    continue

                self.validated.append(key)
                setattr(self, key, value)

            for key in self.attributes:
                if key not in cfg:
                    self.validated.append(key)
                    setattr(self, key, self.__get_default(getattr(self, key)))

            return self

        def __str__(self) -> str:
            return p_value(dict(self), depth=-1)

    return Config


if __name__ == "__main__":

    @config
    class Markdown:
        extensions = TypesDefault(
            list,
            nested_types=[str],
            default=[
                "abbr",
                "admonition",
                "attr_list",
                "def_list",
                "footnotes",
                "md_in_html",
                "tables",
                "toc",
                "wikilinks",
                "codehilite",
                "pymdownx.betterem",
                "pymdownx.caret",
                "pymdownx.details",
                "pymdownx.mark",
                "pymdownx.smartsymbols",
                "pymdownx.superfences",
                "pymdownx.tabbed",
                "pymdownx.tasklist",
                "pymdownx.tilde",
            ],
        )
        extension_configs = {
                "footnotes": {
                    "BACKLINK_TEXT": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 384 512\" class=\"fn-backlink\" style=\"width: .75rem; height: .75rem;\" fill=\"currentColor\"><!--! Font Awesome Pro 6.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path d=\"M32 448c-17.7 0-32 14.3-32 32s14.3 32 32 32l96 0c53 0 96-43 96-96l0-306.7 73.4 73.4c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3l-128-128c-12.5-12.5-32.8-12.5-45.3 0l-128 128c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L160 109.3 160 416c0 17.7-14.3 32-32 32l-96 0z\"/></svg>"
                },
                "codehilite": {"css_class": "highlight"},
            }

    @config
    class Config:
        markdown = Markdown()

    cfg = Config()
    print(cfg)
