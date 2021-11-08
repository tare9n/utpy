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

# Default Settings. The default is like this if you dont define settings.
default_settings = {
    'save_to' : None, # Path to save downloaded video(s) if you want. Read Note (1)
    'file_name' : None, # you can select video files name
    'quality' : None, # Select video quality: 360p or 720p (default: 720p)
    'dl_range' : (), # Define a range to videos in that range in playlist. example: (2, 8) 
    'dl_list' : [], # Select some videos form playlist to download them. example: [5, 7, 8, 12]
    'retries' : 2, # Retries to download video if content not received.
    }

# video or playlist url
url = 'https://www.youtube.com/watch?v=bIGBYOcxMqM' 

# Load utpy!
yt = utpy.Load(url, settings = default_settings)

# return all information as dictionary
yt.data

# download video or videos of playlist
yt.download
```

##### Note (1): Correct save_to formts:

```
{'save_to' : 'D:/path/to/directory'}
or
{'save_to' : r'D:\path\to\directory'}
or
{'save_to' : 'D:\\\path\\\to\\\directory'}
```