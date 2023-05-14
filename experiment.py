class Experiment:
    def __init__(
        self,
        title: str,
        map_file: str,
        x_size: int,
        y_size: int,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        upper_bound: float
    ):
        self._title = title
        self._map_file = map_file
        self._x_size = x_size
        self._y_size = y_size
        self._start_x = start_x
        self._start_y = start_y
        self._end_x = end_x
        self._end_y = end_y
        self._upper_bound = upper_bound

    @property
    def upper_bound(self) -> float:
        return self._upper_bound

    @upper_bound.setter
    def upper_bound(self, upper_bound: float) -> None:
        self._upper_bound = upper_bound

    @property
    def map_file(self) -> str:
        return self._map_file

    @map_file.setter
    def map_file(self, map_file: str) -> None:
        self._map_file = map_file

    @property
    def start_x(self) -> int:
        return self._start_x

    @start_x.setter
    def start_x(self, start_x: int) -> None:
        self._start_x = start_x

    @property
    def start_y(self) -> int:
        return self._start_y

    @start_y.setter
    def start_y(self, start_y: int) -> None:
        self._start_y = start_y

    @property
    def end_x(self) -> int:
        return self._end_x

    @end_x.setter
    def end_x(self, end_x: int) -> None:
        self._end_x = end_x

    @property
    def end_y(self) -> int:
        return self._end_y

    @end_y.setter
    def end_y(self, end_y: int) -> None:
        self._end_y = end_y

    @property
    def x_size(self) -> int:
        return self._x_size

    @property
    def y_size(self) -> int:
        return self._y_size
    
    @property
    def title(self) -> str:
        return self._title
