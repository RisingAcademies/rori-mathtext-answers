if [ -f ".env" ] ; then
    source .env
fi

if [ -f ".venv/bin/activate" ] ; then
    source .venv/bin/activate
fi

pip install --upgrade pip poetry virtualenv wheel
pip install --upgrade -e .

# pip install --upgrade scikit-learn
# pip install --upgrade transformers
# pip install --upgrade pandas
