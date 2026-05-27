import matplotlib.widgets as widgets
import matplotlib.pyplot as plt
import numpy as np


class Visualize:
    """A simple wrapper around matplotlib for quick signal visualization."""

    def __init__(self, title: str, y_label: str, x_label: str = "Time (s)", grid: bool = True):
        """Create a new plot window.

        Args:
            title: Title displayed above the plot.
            y_label: Label for the y-axis.
            x_label: Label for the x-axis. Defaults to "Time (s)".
            grid: Whether to show a grid. Defaults to True."""
        self.title = title
        self._x_label = x_label
        self._y_label = y_label
        self._grid = grid
        self._signals: list[dict] = []
        self._current_n: int = 0
        self._xlim: tuple[float, float] = (0.0, 1.0)
        self._ylim: tuple[float, float] = (0.0, 1.0)
        self._locking: bool = False
        self._video_sequence: np.ndarray | None = None
        self._fig, self._ax = plt.subplots()
        self._ax.set_title(title)
        self._ax.set_xlabel(x_label)
        self._ax.set_ylabel(y_label)
        self._ax.grid(grid)

    def add_signal(self, y_axis: np.ndarray, x_axis: np.ndarray | None = None, label: str = "", color: str | None = None, scatter: bool = False):
        """Add a signal to the plot.

        Args:
            y_axis: Signal values to plot.
            x_axis: Corresponding x values. If None, uses index range of y_axis.
            label: Legend label for this signal.
            color: Line or marker color. If None, uses matplotlib's default color cycle.
            scatter: If True, renders as a scatter plot instead of a line."""
        if x_axis is None:
            x_axis = np.arange(len(y_axis))

        sig: dict = {"y": y_axis, "x": x_axis, "label": label, "color": color, "scatter": scatter, "visible": True}
        self._signals.append(sig)

        if scatter:
            artist = self._ax.scatter(x_axis, y_axis, label=label, color=color)
            sig["color"] = artist.get_facecolor()[0]
        else:
            (line,) = self._ax.plot(x_axis, y_axis, label=label, color=color)
            sig["color"] = line.get_color()

        self._update_legend()

    def _update_legend(self):
        """Rebuild the legend and make each handle pickable."""
        labeled = [sig for sig in self._signals if sig["label"]]
        if not labeled:
            return
        legend = self._ax.legend(loc="upper left")
        for handle, sig in zip(legend.legend_handles, labeled):
            if handle is None:
                continue
            handle.set_picker(8)
            handle.set_alpha(1.0 if sig["visible"] else 0.3)

    def _redraw(self, n: int):
        """Redraw all signals truncated to the first n points.

        Args:
            n: Number of points to show from the start of each signal."""
        self._current_n = n
        self._ax.cla()
        self._ax.set_title(self.title)
        self._ax.set_xlabel(self._x_label)
        self._ax.set_ylabel(self._y_label)
        self._ax.grid(self._grid)
        for sig in self._signals:
            if not sig["visible"]:
                if sig["scatter"]:
                    self._ax.scatter([], [], label=sig["label"], color=sig["color"])
                else:
                    self._ax.plot([], [], label=sig["label"], color=sig["color"])
                continue
            x, y = sig["x"][:n], sig["y"][:n]
            if sig["scatter"]:
                self._ax.scatter(x, y, label=sig["label"], color=sig["color"])
            else:
                self._ax.plot(x, y, label=sig["label"], color=sig["color"])
        self._update_legend()
        self._ax.set_xlim(self._xlim)
        self._ax.set_ylim(self._ylim)
        if self._video_sequence is not None:
            frame_idx = min(n - 1, len(self._video_sequence) - 1)
            video_ax = self._ax.inset_axes((0.62, 0.55, 0.36, 0.42))
            video_ax.axis("off")
            video_ax.imshow(self._video_sequence[frame_idx], aspect="auto")
        self._fig.canvas.draw_idle()

    def show(self, slider: bool = False, video_sequence: np.ndarray | None = None):
        """Render and display the plot in a window.

        Args:
            slider: If True, adds a slider to step through points one by one.
            video_sequence: Optional array of shape (n_frames, H, W) or (n_frames, H, W, C).
                            Each frame is shown in the upper-right corner at the corresponding
                            slider position. Number of frames must match the signal length."""
        if not self._signals:
            self._fig.tight_layout()
            plt.show()
            return

        self._current_n = max(len(sig["y"]) for sig in self._signals)

        x_all = np.concatenate([sig["x"] for sig in self._signals])
        y_all = np.concatenate([sig["y"] for sig in self._signals])
        margin = (y_all.max() - y_all.min()) * 0.05 or 0.05
        self._xlim = (float(x_all.min()), float(x_all.max()))
        self._ylim = (float(y_all.min() - margin), float(y_all.max() + margin))
        self._ax.set_xlim(self._xlim)
        self._ax.set_ylim(self._ylim)

        def _on_lim_change(_: object) -> None:
            if not self._locking:
                self._locking = True
                self._ax.set_xlim(self._xlim)
                self._ax.set_ylim(self._ylim)
                self._locking = False

        self._ax.callbacks.connect("xlim_changed", _on_lim_change)
        self._ax.callbacks.connect("ylim_changed", _on_lim_change)

        if video_sequence is not None:
            self._video_sequence = video_sequence

        def _on_pick(event: object) -> None:
            legend = self._ax.get_legend()
            if legend is None:
                return
            handles = list(legend.legend_handles)
            if event.artist not in handles:  # type: ignore[union-attr]
                return
            labeled = [sig for sig in self._signals if sig["label"]]
            idx = handles.index(event.artist)  # type: ignore[union-attr]
            labeled[idx]["visible"] = not labeled[idx]["visible"]
            self._redraw(self._current_n)

        self._fig.canvas.mpl_connect("pick_event", _on_pick)

        if slider:
            self._fig.subplots_adjust(bottom=0.15)
            ax_slider = self._fig.add_axes((0.1, 0.04, 0.8, 0.03))
            sl = widgets.Slider(ax_slider, "", 1, self._current_n, valinit=self._current_n, valstep=1)
            sl.on_changed(lambda val: self._redraw(int(val)))
        else:
            self._fig.tight_layout()

        self._redraw(self._current_n)
        plt.show()

    def save(self, path: str):
        """Save the plot to a file.

        Args:
            path: Destination file path (e.g. "plot.png", "plot.pdf")."""
        self._fig.tight_layout()
        self._fig.savefig(path)


if __name__ == "__main__":
    t = np.linspace(0, 2 * np.pi, 200)

    viz = Visualize("All Features Demo", y_label="Amplitude")
    viz.add_signal(np.sin(t), x_axis=t, label="sin(t)")
    viz.add_signal(np.cos(t), x_axis=t, label="cos(t)", color="orange")
    viz.add_signal(np.abs(np.sin(t)) * 0.5, x_axis=t, label="|sin(t)| * 0.5", color="green", scatter=True)
    viz.add_signal(np.sin(t) * 0.7, x_axis=t[::-1], label="sin(t) reversed x", color="purple")
    rng = np.random.default_rng(42)
    x_rand = rng.uniform(t.min(), t.max(), len(t))
    viz.add_signal(np.sin(x_rand), x_axis=x_rand, label="sin random x", color="brown", scatter=True)
    xs = np.linspace(0, 2 * np.pi, 64)
    frames = np.array([np.outer(np.sin(xs + t[i]), np.cos(xs + t[i])) for i in range(len(t))])

    viz.show(slider=True, video_sequence=frames)
