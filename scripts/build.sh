deactivate
pip install --upgrade pytest-cov wheel pip virtualenv build
rm -rf .venv
python3.9 -m virtualenv --python 3.9 .venv
source .venv/bin/activate
# pip install --upgrade scikit-learn
# pip install --upgrade transformers
# pip install --upgrade pandas
pip install --upgrade -e .
