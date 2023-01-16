deactivate
pip install virtualenv
rm -rf .venv
python3.9 -m virtualenv --python 3.9 .venv
# pip install --upgrade scikit-learn
# pip install --upgrade transformers
# pip install --upgrade pandas
pip install --upgrade -e .
