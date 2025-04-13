import typing
from pathlib import Path

from vqaopt.core.plugin import Field

from .load_acp_csv import LoadACP_CSV


class LoadACPExample(LoadACP_CSV):
    input_dir_location: str = "."
    import_from: str = Field(exclude=True, default="input/example/legs.csv")

    @classmethod
    def get_name(cls) -> str:
        return "Load ACP Example"

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.import_from = str(Path(self.input_dir_location) / self.import_from)
