# EasyPlot

A lightweight Python wrapper around [matplotlib](https://matplotlib.org/) for quick signal visualization with minimal boilerplate.

## Features

- Plot multiple signals (line or scatter) with a single method call
- Interactive slider to step through data points one by one
- Clickable legend to toggle signal visibility
- Optional synchronized video frame overlay (upper-right corner)
- Save plots to file (PNG, PDF, ...)

## Installation

Requires Python >= 3.11. Install dependencies with [uv](https://github.com/astral-sh/uv):

```bash
uv sync
```

Or with pip:

```bash
pip install matplotlib numpy
```

## Usage

```python
import numpy as np
from src.Visualize.Visualize import Visualize

t = np.linspace(0, 2 * np.pi, 200)

viz = Visualize("My Plot", y_label="Amplitude", x_label="Time (s)")
viz.add_signal(np.sin(t), x_axis=t, label="sin(t)")
viz.add_signal(np.cos(t), x_axis=t, label="cos(t)", color="orange")
viz.show()
```

### Slider mode

Pass `slider=True` to `show()` to add a slider that steps through the data:

```python
viz.show(slider=True)
```

### Video overlay

Pass a `(n_frames, H, W)` or `(n_frames, H, W, C)` array to overlay video frames synchronized to the slider position:

```python
frames = np.random.rand(200, 64, 64)
viz.show(slider=True, video_sequence=frames)
```

### Save to file

```python
viz.save("plot.png")
```

## API

### `Visualize(title, y_label, x_label="Time (s)", grid=True)`

Creates a new plot window.

### `add_signal(y_axis, x_axis=None, label="", color=None, scatter=False)`

Adds a signal to the plot. If `x_axis` is `None`, the index range of `y_axis` is used.

### `show(slider=False, video_sequence=None)`

Displays the plot. Optionally adds a slider and/or a video overlay.

### `save(path)`

Saves the plot to the given file path.
