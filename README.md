# badminton_booking

## Setting

1. Update `.example_env` rename to `.env`
2. Set your line notify token

## Setup your env

### Install tesseract

Please reference to the [documentation](https://github.com/madmaze/pytesseract#installation), or you can use the following command to install on macOS:

```
brew install tesseract
```

### Install package

```
pipenv install
```

### Setup the pre-commit
```
pre-commit install
```

### Check all file by pre-commit
```
pre-commit run --all-files
```

### Run script with virtual env

```
pipenv shell
```

```
python app.py
```
