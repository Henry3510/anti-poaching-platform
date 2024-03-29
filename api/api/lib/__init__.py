from functools import wraps
from inspect import Parameter, signature
from typing import Any, Callable, Iterable, List, OrderedDict, Type, TypeVar, get_origin
from weakref import WeakValueDictionary

from fastapi import Query
from pydantic.main import BaseModel

T = TypeVar("T")


def to_camel(string: str) -> str:
    """
    Convert a string to camelcase by capitalizing the first characters
    in each word of a snakecase string after removing leading underscores
    """
    string = string.lstrip("_")
    words = [word for word in string.title() if not word.isspace() and not word == "_"]
    return words[0].lower() + "".join(words[1:])


def to_snake(string: str) -> str:
    """
    Convert a string to snakecase by uncapping uppercase characters
    and inserting an underscore for each occurence
    """
    string = "".join(
        [f"{'_' if char.isupper() else ''}{char.lower()}" for char in string]
    )
    string = string.lstrip("_")
    return string


class APIModel(BaseModel):
    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True


def get_unique_attributes(
    objs: Iterable[T], attributes: Iterable[str]
) -> OrderedDict[str, tuple[set[Any], WeakValueDictionary[Any, T]]]:
    """Find the unique attributes of a list of given object

    Args:
        objs (Iterable[T]): The objects to be processed
        attributes (Iterable[str]): The attributes to be looked up

    Returns:
        tuple[OrderedDict[str, tuple[set[Any], WeakValueDictionary[Any, T]]]]: \
            An ordered dictionary containing: \
                a unique set for each of the attributes preserving the order of the attributes; \
                and a WeakValueDictionary containing a mapping from the value of the attributes \
                    to the original objects.
    """
    result = OrderedDict()
    for attribute in attributes:
        ref: WeakValueDictionary[Any, T] = WeakValueDictionary()
        unique_set = set()
        for obj in objs:
            val = getattr(obj, attribute)
            ref[val] = obj
            unique_set.add(val)
        result[attribute] = (unique_set, ref)
    return result


def map_attribute(
    objects: Iterable[object], source_key: str, value_key: str
) -> dict[str, Any]:
    """Map one attribute to another for a list of objects

    Args:
        objects (Iterable[object]): The objects to be mapped
        source_key (str): The key of the attribute that will be mapped FROM
        value_key (str): The key of the attribute that will be mapped TO

    Returns:
        dict[str, Any]: The mapped dictionary
    """
    return {getattr(obj, source_key): getattr(obj, value_key) for obj in objects}


ModelT = TypeVar("ModelT", bound=APIModel)


def has_query_params(model: Type[ModelT]) -> Callable[..., ModelT]:
    """Autogenerate a function for APIModel with list fields default to Query(None)
    The motive behind this function is to allow the use of lists in query parameters with a Pydantic model,
    which is otherwise considered a part of the request body by FastAPI.

    Note that this will not attempt to resolve dependencies.
    In nested APIModel for query parameters, use Depends(has_query_params(SomeModel)) instead of Depends(SomeModel).

    Args:
        model (ModelT): The original model that contains lists

    Returns:
        Callable[..., ModelT]: A function that has all the fields of the model as arguments and returns ModelT
    """

    # Grab the signature of the original function
    sig = signature(model)
    params = []
    defaults = {}
    for _, field in model.__fields__.items():
        # We need to origin to determine if the field is a list or not
        origin = get_origin(field.outer_type_)
        if origin is not None and issubclass(origin, List):
            if not field.allow_none and field.default is None:
                # Pydantic should handle a mutable list as the default value correctly
                default = Query(origin())
            else:
                default = Query(field.default)
        else:
            default = field.default
        # Add the new parameter with the default value replaced
        param = Parameter(
            field.alias,
            Parameter.KEYWORD_ONLY,
            default=default,
            annotation=field.outer_type_,
        )
        defaults[field.alias] = default
        params.append(param)

    # Override the signature of the wrapper function using the new parameters
    def wrapper(*args, **kwargs) -> ModelT:
        return model(*args, **kwargs)

    setattr(wrapper, "__signature__", sig.replace(parameters=params))
    return wrapper
