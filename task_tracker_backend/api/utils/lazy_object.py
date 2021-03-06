from typing import TypeVar, Type, Optional

T = TypeVar('T')


class LazyObject:
    """
    Allows delaying initialization of object.
    """

    def __init__(self, _class: Type[T], *args, **kwargs) -> None:
        """
        Allows delaying initialization of object.

        :param _class: Instance of this class will be created.
        :param args: Args of constructor.
        :param kwargs: Kwargs of constructor.
        """
        self.__args = args
        self.__kwargs = kwargs

        self.__class = _class
        self.__object: Optional[T] = None

    async def __call__(self) -> T:
        if self.__object is None:
            self.__object = self.__class(*self.__args, **self.__kwargs)

        return self.__object
