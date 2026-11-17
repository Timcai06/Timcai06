"""Shared presentation tokens for Tim Cai's profile exhibition panels."""
WIDTH = 1800
MARGIN = 80
DISPLAY_SIZE = 170
CAPTION_SIZE = 24
HERO_RADIUS = 14
DETAIL_RADIUS = 8
SLIDE_SECONDS = 4
FADE_SECONDS = 0.5


def palette(light=False):
    return ({'ink': '#24292f', 'muted': '#57606a', 'rail': '#d0d7de', 'frame': '#b7bec6'}
            if light else
            {'ink': '#e6edf3', 'muted': '#9da7b3', 'rail': '#303943', 'frame': '#424a54'})
