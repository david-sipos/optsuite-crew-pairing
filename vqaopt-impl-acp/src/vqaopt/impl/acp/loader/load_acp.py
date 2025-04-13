"""
Load ACP instance from the input directory.
"""

import typing
from pathlib import Path

from vqaopt.core.plugin import Field

from .load_acp_csv import LoadACP_CSV


class LoadACP(LoadACP_CSV):
    """
    Load ACP instance from the input directory.
    """

    input_dir_location: str = "."
    instance: typing.Literal[
        "instance_1",
        "instance_2",
        "instance_3",
        "instance_4",
        "instance_5",
        "instance_6",
        "instance_7",
    ]
    days: int = Field(
        default=31,
        title="How many days to include (1-31)",
        ge=1,
        le=31,
    )

    @classmethod
    def get_name(cls) -> str:
        return "Load ACP"

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.import_from = [
            str(
                Path(self.input_dir_location) / "input" / f"{self.instance}/day_{i}.csv"
            )
            for i in range(1, self.days + 1)
        ]
