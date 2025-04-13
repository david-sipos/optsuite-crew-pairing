import csv
import typing

from ..data_model import Leg, LegContainer


def load_legs_from_file(
    process_row: typing.Callable[[typing.Sequence[str]], Leg],
    path: str,
    reader_kwargs: dict[str, typing.Any] | None = None,
    skip_header: bool = True,
) -> LegContainer:
    """
    Loads the csv at `path` into a LegContainer.

    Parameters
    ----------
    `path` : str
        The path to the csv file
    `reader_kwargs`: dict[str, Any] | None, defaults to None
        Keyword arguments to pass to the `csv.reader`.
    `proc` : Callable[[Sequence[str]], Leg] | None, defults to None
        A function that turns a single row of the csv file into a Leg.
        See default behaviour below.
    `skip_header` : bool, defaults to True
        If True, skips the first line.

    The default row processing assumes no flight transports and the following columns in the file:
    - Flight Number
    - Departure Airport
    - Departure Date (%Y-%m-%d)
    - Departure Time (%H:%M)
    - Arrival Airport
    - Arrival Date (%Y-%m-%d)
    - Arrival Time (%H:%M)
    """

    with open(path, "r", encoding="utf-8") as f:
        if reader_kwargs is None:
            reader = csv.reader(f)
        else:
            reader = csv.reader(f, **reader_kwargs)

        if skip_header:
            next(reader, None)

        legs: list[Leg] = [process_row(row) for row in reader]

    container = LegContainer(legs)

    return container
