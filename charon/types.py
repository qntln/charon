from typing import Callable, List, Dict, Tuple, Any, Union



VersionType = Union[int, None]
BaseType = Union[int, float, bool, str, bytes, None, List[Any], Dict[Any, Any], Tuple[Any]]

EncodingType = Dict[str, Any]
CoderType = Callable[[Any], BaseType]
