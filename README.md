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
default_settings = {
    'save_to' : None, # Path to save downloaded video(s) if you want. Read Note (1)
    'file_name' : None, # you can select video files name
    'retries' : 2, # Number of retries if videos content not received.
    } # More settings in next version -Insha'Allah-
url = 'https://www.youtube.com/watch?v=bIGBYOcxMqM' # video or playlist url
yt = utpy.Load(url, settings = default_settings)

# return all information as dictionary
yt.data

# download video or videos of playlist
yt.download
```

##### Note (1): Correct save path formts:
```
save_to =  'D:/path/to/directory'
or
save_to = r'D:\path\to\directory'
or
save_to = 'D:\\\path\\\to\\\directory'
```