# utpy

simple python library for download youtube video or playlist.

utpy = U (you) - T (Tube) - PY (python)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install utpy.

```bash
pip install utpy
```

## Usage

```python
import utpy

url = 'https://www.youtube.com/watch?v=bIGBYOcxMqM' # video or playlist url
yt = utpy.Load(url)

# return all information as dic
yt.data

# download video or videos of playlist
yt.download()

```