```sh
uv run python -m ipykernel install --user --name=reports --display-name="Python (reports)"
uv run ipython kernel install --user --env VIRTUAL_ENV ${pwd}/.venv --name quarto_report

source .venv/bin/activate && python -m ipykernel install --user --name=reports --display-name="Python (reports)"

source .venv/bin/activate

quarto preview index.qmd --no-browser --no-watch-inputs

```