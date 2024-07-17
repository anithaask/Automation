# This file is run by ./github/workflows/main.yaml as part of GitHub Actions

# See bash options here: https://tldp.org/LDP/abs/html/options.html
set -eux

pip install poetry

# Have to add this so that the fuel python package will work. It stores logs in the path provided by the TEMP variable
export TEMP="./"

jfrog rt pipc --server-id-resolve "Default-Server" --repo-resolve "cfr-pypi-releases-group"
jfrog rt pipi cfrpos
jfrog rt pipi sim4cfrpos
jfrog rt pipi cfrfuelbdd
jfrog rt pipi cfrsc
jfrog rt pipi cfrsmtaskman
jfrog rt pipi rpos_bdd_tools
jfrog rt pipi relay_configuration

poetry env info
poetry config virtualenvs.create false
poetry install -vvv

python -m behave sitbdd --dry-run --tags ~@wip

# poetry run pre-commit run --all-files --show-diff-on-failure
# poetry pytest --verbose --cov=sitbdd

var1=$(cat ./Version)
poetry version $var1
poetry build --format wheel

mkdir -p Distribution/pypi
mv dist/* Distribution/pypi
cp one_click_setup.py Distribution/
cp run_bdd.py Distribution/

