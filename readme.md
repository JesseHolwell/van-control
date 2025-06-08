# Van Control

## Goals:

Display environment info

Display van sensor data

Provide interface to toggle GPIO pins

## Constraints:

Ultra low power

Doesn't always have an internet connection

Fit on a galaxy a8 tablet in landscape

## Plan

Python flask website

Auto refresh (60s)

Request and save weather data when internet is available

Fully Kiosk Browser running on the tablet

## Development

```sh
python3 -m venv venv
source venv/bin/activate
pip install requirements
python app.py
```
