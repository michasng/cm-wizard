# Cardmarket wizard

A wizard that helps you find the cheapest prices for cards on you wants lists.
This project is inspired by and in part based on [cw-wizard](https://github.com/BenSouchet/cw-wizard).

## Getting Started

### Prerequisites

You need [Poetry](https://python-poetry.org/docs/).

### Installation

Install dependencies (including development dependencies):

```bash
poetry install
poetry run pre-commit install
```

If you don't need development depdencies, run:

```bash
poetry install --without dev
```

### Running

Run without hot reload:

```bash
poetry run python -m cm_wizard
```

Run with hot reload (so code changes are automatically reflected by the application):

```bash
poetry run flet run -m -r cm_wizard
```

### Running the tests

TODO

### Run pre-commit hooks

Manually run pre-commit hooks for static type checking and formatting.

```bash
poetry run pre-commit run --all-files
```

### Static type checking

Check for type errors:

```bash
poetry run mypy .
```

### Formatting

Sort imports:

```bash
poetry run isort .
```

Format code:

```bash
poetry run black .
```

Note that `isort` and `black` apply some conflicting changes.
For now, `isort` should be used first and then `black` should run afterwards.

Most IDEs can be configured to have hotkeys for these actions.
For VSCode on Windows, press Alt + Shift + O to sort imports and Alt + Shift + F to format code.

## Versioning

We use [Semantic Versioning](http://semver.org/) for versioning. For the versions
available, see the [tags on this
repository](https://github.com/PurpleBooth/a-good-readme-template/tags).

## Authors

  - **Micha Sengotta**
    [michasng](https://github.com/michasng)

## License

The code present in this repository is under [MIT license](https://github.com/michasng/cm-wizard/blob/main/LICENSE).

## Acknowledgments

  - **Ben Souchet**
    Creator of the original cw-wizard
    [BenSouchet](https://github.com/BenSouchet)
