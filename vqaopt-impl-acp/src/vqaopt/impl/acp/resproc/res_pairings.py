"""Visualize the solution on the graph."""

import itertools
import typing
from datetime import datetime, timedelta
from functools import reduce
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patches

from vqaopt.core.plugin import Ansatz, Field, Optimizer, ResProc
from vqaopt.core.plugin.platform import VQAResult

from ..acp_problem import ACPProblem

Leg = tuple[str, datetime, str, datetime]
Pairing = list[Leg]


class ResAcpPairings(ResProc):
    """Visualize the solution on the graph."""

    figsize: tuple = Field(
        default=(20, 8),
        title="Figure size",
    )
    format: typing.Literal["png", "pdf"] = Field(
        default="pdf",
        title="Format",
    )
    file_name: str = Field(
        default="pairings",
        title="File name",
    )
    date_label_size: int = Field(
        default=18,
        title="Date label size",
    )
    axis_label_size: int = Field(
        default=20,
        title="Axis label size",
    )
    tick_label_size: int = Field(
        default=18,
        title="Tick label size",
    )

    @classmethod
    def get_name(cls) -> str:
        return "ACP Pairings"

    def after_problem(
        self,
        runtime: float,
        problem: ACPProblem,
        ansatz: Ansatz,
        optimizer: Optimizer,
        data: VQAResult,
        out_folder: Path | None,
    ) -> list[Pairing] | None:
        if ACPProblem.get_name() not in problem.forms:
            return None
        problem = problem.forms[ACPProblem.get_name()]

        most_likely_bitstring = max(
            data.final_counts, key=lambda k: data.final_counts[k]
        )

        pairings: list[Pairing] = []
        for pairing in problem.pairings_from_bitstring(most_likely_bitstring):
            pairings.append([])
            for duty in pairing.duties:
                for leg1, leg2 in itertools.pairwise(duty.legs):
                    pairings[-1].append(
                        (
                            leg1.departure_airport,
                            leg1.departure_datetime,
                            leg1.arrival_airport,
                            leg1.arrival_datetime,
                        )
                    )
                    pairings[-1].append(
                        (
                            leg2.departure_airport,
                            leg2.departure_datetime,
                            leg2.arrival_airport,
                            leg2.arrival_datetime,
                        )
                    )
        return pairings

    def _setup_figure(
        self,
        fig: plt.Figure,
        airport_to_idx: list[str],
        first_dt: datetime,
    ) -> None:
        for idx, ax in enumerate(fig.get_axes()):
            ax.set_title(
                str(first_dt.date() + timedelta(days=idx)), size=self.date_label_size
            )
            ax.tick_params(labelsize=self.tick_label_size)
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

        fig.supylabel("Airport", size=self.axis_label_size)
        fig.supxlabel("Time", size=self.axis_label_size)
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
        first_dt, last_dt = reduce(
            lambda x, y: (min(x[0], y[1]), max(x[1], y[3])),
            (leg for legs in pairings for leg in legs),
            (datetime.max, datetime.min),
        )
        number_of_days = (last_dt.date() - first_dt.date()).days + 1

        fig, _ = plt.subplots(ncols=number_of_days, figsize=self.figsize, sharey=True)
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
        pairings_list: list[list[Pairing]],
        out_folder: Path | None,
    ) -> typing.Any:
        for i, pairings in enumerate(pairings_list):
            fig = self.plot(pairings)
            if out_folder is not None:
                fig.savefig(out_folder / f"{self.file_name}_{i}.{self.format}")
            else:
                fig.savefig(f"{self.file_name}_{i}.{self.format}")
            plt.close(fig)
