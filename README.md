# Cardmarket wizard

Improved cardmarket shopping wizard! 🧙‍♂️  
Find the best combination of sellers for cards on your wants lists. 🪄

This project is inspired by and in part based on [cw-wizard](https://github.com/BenSouchet/cw-wizard). Check it out!

## ⚠️ Important notice ⚠️

This project is discontinued, because it is no longer possible to skip cardmarket's cloudflare protection by using cookies from another browser.  
I am exploring ways around this, which will be implemented in a re-write of this project.

## Features

- Browse your wants lists. ✅
- Find the best prices. ✅
- Supports all card games on cardmarket. ⚠️ Currently only Yu-Gi-Oh!.
- Open Source, MIT Licensed. Clean, easy to read code. ✅

## Installation & Running

You need [Poetry](https://python-poetry.org/docs/) installed.

Install production dependencies:

```bash
poetry install --without dev
```

Run the application:

```bash
poetry run python -m cm_wizard
```

## Development

Install dependencies (including development dependencies) and pre-commit hooks:

```bash
poetry install
poetry run pre-commit install
```

Run with hot reload (meaning the application reloads after code changes):

```bash
poetry run flet run -m -r cm_wizard
```

### Tests

```bash
poetry run pytest tests
```

### Code Analysis

Manually run all pre-commit hooks:

```bash
poetry run pre-commit run --all-files
```

Or run them individually:

- Static type checks: `poetry run mypy .`
- Sort imports: `poetry run isort .`
- Format code: `poetry run black .`

## Authors

- **Micha Sengotta**
  [michasng](https://github.com/michasng)

## License

The code present in this repository is under [MIT license](https://github.com/michasng/cm-wizard/blob/main/LICENSE).

## Acknowledgments

- **Ben Souchet**
  [BenSouchet](https://github.com/BenSouchet)  
  Creator of the original cw-wizard. Thank You! 💫
