"""Visualize the solution on the graph."""

import itertools
import typing
from datetime import datetime, timedelta
from functools import reduce
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from matplotlib import patches

from vqaopt.core.plugin import Field, ResProc
from vqaopt.core.problem import Problem
from vqaopt.impl.problems import IsingProblem
from vqaopt.impl.utils.folder import get_folders

from ..acp_problem import ACPProblem


class ResAcpPairings(ResProc):
    """Visualize the solution on the graph."""

    width: float = Field(default=6, title="Width")
    scale: float = Field(
        default=0.5,
        title="Scale",
    )
    aspect: float = Field(
        default=0.5,
        title="Aspect",
    )
    style: list[str] = Field(default_factory=list, title="Scienceplots style")
    rc_params: dict = Field(default_factory=dict, title="MPL rc params")
    file_name: str = Field(
        default="pairings",
        title="File name",
    )
    to_plot: typing.Literal["all", "most-likely", "best"] = Field(
        default="most-likely", title="Pairings to visualize"
    )
    format: typing.Literal["png", "pdf", "pgf"] = Field(
        default="pdf",
        title="Format",
    )

    @classmethod
    def get_name(cls) -> str:
        return "ACP Pairings"

    def after_problem(
        self,
        problem: Problem,
        run_info: dict,
        experiment_config,
        result: dict,
        experiment_folder: Path | None,
    ) -> tuple[dict[str, typing.Any], list[dict[str, typing.Any]]] | None:
        if ACPProblem.get_name() not in problem.forms:
            return None
        if "final_counts" not in result:
            return None

        problem = problem.forms[ACPProblem.get_name()]
        ising = problem.forms[IsingProblem.get_name()]
        run_indices: dict[str, typing.Any] = run_info.get("run_indices", {})

        return run_indices, [
            {
                "bitstring": k,
                "count": v,
                "cost": problem.cost_of_bitstring(k),
                "ising_cost": ising.cost_of_bitstring(k),
                "pairings": list(problem.pairings_from_bitstring(k)),
            }
            for k, v in result["final_counts"].items()
        ]

    def _setup_figure(
        self,
        fig: plt.Figure,
        airport_to_idx: list[str],
        first_dt: datetime,
    ) -> None:
        for idx, ax in enumerate(fig.get_axes()):
            ax.set_title(str(first_dt.date() + timedelta(days=idx)))
            ax.set_xticks(range(0, 24 * 60 + 1, 60))
            ax.set_xticklabels([f"{h:02d}:00" for h in range(0, 25)], rotation=45)
            ax.set_yticks(range(len(airport_to_idx)))
            ax.set_yticklabels(airport_to_idx)
            ax.xaxis.grid(True)

            for i in range(len(airport_to_idx)):
                ax.axhline(
                    i - 0.4,
                    color="black",
                    linestyle="--",
                )
                ax.axhline(
                    i + 0.4,
                    color="black",
                    linestyle="--",
                )

        fig.supylabel("Airport")
        fig.supxlabel("Time")
        plt.tight_layout()

    def _airport_to_value(
        self, idx_airport: int, idx_pairing: int, len_pairings: int
    ) -> float:
        step = (np.ceil(idx_pairing / 2)) / len_pairings
        return idx_airport + 0.8 * (
            step * ((idx_pairing % 2) * 2 - 1)
            - 0.5 * (1 - len_pairings % 2) / len_pairings
        )

    def plot(
        self, pairings: list[list[tuple[str, datetime, str, datetime]]]
    ) -> plt.Figure:
        height = self.width / self.aspect

        def red(
            acc: tuple[datetime, datetime], elem: tuple[str, datetime, str, datetime]
        ):
            first_dt, last_dt = acc
            _, arr_dt, _, dep_dt = elem
            return (min(first_dt, arr_dt), max(last_dt, dep_dt))

        first_dt, last_dt = reduce(
            red,
            (leg for legs in pairings for leg in legs),
            (datetime.max, datetime.min),
        )
        number_of_days = (last_dt.date() - first_dt.date()).days + 1

        fig, _ = plt.subplots(
            ncols=number_of_days,
            figsize=(height * self.scale, self.width * self.scale),
            sharey=True,
        )
        axs = fig.get_axes()

        colors = plt.cm.get_cmap("hsv")(np.linspace(0, 1, len(pairings) + 1))

        airport_to_idx = sorted(
            set(leg[0] for pairing in pairings for leg in pairing)
            | set(leg[2] for pairing in pairings for leg in pairing)
        )
        self._setup_figure(fig, airport_to_idx, first_dt)
        for idx_pairing, legs in enumerate(pairings):
            for (
                start_point,
                start_dt,
                end_point,
                end_dt,
            ) in legs:
                day_st = start_dt.day - first_dt.day
                day_ed = end_dt.day - first_dt.day
                axs[day_st].plot(
                    start_dt.hour * 60 + start_dt.minute,
                    self._airport_to_value(
                        airport_to_idx.index(start_point), idx_pairing, len(pairings)
                    ),
                    "o",
                    color=colors[idx_pairing],
                )
                axs[day_ed].plot(
                    end_dt.hour * 60 + end_dt.minute,
                    self._airport_to_value(
                        airport_to_idx.index(end_point), idx_pairing, len(pairings)
                    ),
                    "o",
                    color=colors[idx_pairing],
                )
        fig.canvas.draw()

        for idx_pairing, legs in enumerate(pairings):
            for i, (
                start_point,
                start_dt,
                end_point,
                end_dt,
            ) in enumerate(legs):
                ax1 = start_dt.day - first_dt.day
                nx1, ny1 = axs[ax1].transData.transform(
                    (
                        start_dt.hour * 60 + start_dt.minute,
                        self._airport_to_value(
                            airport_to_idx.index(start_point),
                            idx_pairing,
                            len(pairings),
                        ),
                    )
                )
                x1, y1 = fig.transFigure.inverted().transform((nx1, ny1))
                ax2 = end_dt.day - first_dt.day
                nx2, ny2 = axs[ax2].transData.transform(
                    (
                        end_dt.hour * 60 + end_dt.minute,
                        self._airport_to_value(
                            airport_to_idx.index(end_point),
                            idx_pairing,
                            len(pairings),
                        ),
                    )
                )
                x2, y2 = fig.transFigure.inverted().transform((nx2, ny2))
                arrow = patches.FancyArrowPatch(
                    (x1, y1),
                    (x2, y2),
                    transform=fig.transFigure,
                    arrowstyle=patches.ArrowStyle.Simple(head_length=8, head_width=5),
                    color=colors[idx_pairing],
                )
                fig.add_artist(arrow)

                if i != 0:
                    (_, _, end_point, end_dt) = legs[i - 1]
                    ax0 = end_dt.day - first_dt.day
                    nx0, ny0 = axs[ax0].transData.transform(
                        (
                            end_dt.hour * 60 + end_dt.minute,
                            self._airport_to_value(
                                airport_to_idx.index(end_point),
                                idx_pairing,
                                len(pairings),
                            ),
                        )
                    )
                    x0, y0 = fig.transFigure.inverted().transform((nx0, ny0))
                    arrow = patches.FancyArrowPatch(
                        (x0, y0),
                        (x1, y1),
                        transform=fig.transFigure,
                        arrowstyle="-",
                        color=colors[idx_pairing],
                    )
                    fig.add_artist(arrow)

        return fig

    def after_experiment(
        self,
        aggr: list[tuple[dict[str, typing.Any], list[dict[str, typing.Any]]]],
        experiment_folder: Path | None,
    ) -> typing.Any:

        with plt.style.context(self.style):
            with mpl.rc_context(self.rc_params):
                for i, (run_indices, results) in enumerate(aggr):
                    match self.to_plot:
                        case "best":
                            results = [min(results, key=lambda d: d["ising_cost"])]
                        case "most-likely":
                            results = [max(results, key=lambda d: d["count"])]

                    for result in results:
                        if int(result["bitstring"], 2) == 0:
                            continue

                        plot_data: list[list[tuple[str, datetime, str, datetime]]] = []
                        pairings = result["pairings"]
                        for pairing in pairings:
                            plot_data.append([])
                            for leg1, leg2 in itertools.pairwise(pairing.legs_iterator):
                                plot_data[-1].append(
                                    (
                                        leg1.departure_airport,
                                        leg1.departure_datetime,
                                        leg1.arrival_airport,
                                        leg1.arrival_datetime,
                                    )
                                )
                                plot_data[-1].append(
                                    (
                                        leg2.departure_airport,
                                        leg2.departure_datetime,
                                        leg2.arrival_airport,
                                        leg2.arrival_datetime,
                                    )
                                )
                        fig = self.plot(plot_data)

                        _, _, repetition_folder = get_folders(
                            experiment_folder or Path.cwd(),
                            **run_indices,
                        )
                        repetition_folder.mkdir(parents=True, exist_ok=True)

                        fig.savefig(
                            repetition_folder
                            / f"{self.file_name}_{i}_{int(result["bitstring"],2)}.{self.format}"
                        )

                        plt.close(fig)
