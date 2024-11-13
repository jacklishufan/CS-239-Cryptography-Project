apt install -y python3.9-venv python3.9-dev
mkdir ~/.venvs
rm -rf ~/.venvs/cs239
python3.9 -m venv ~/.venvs/cs239
source ~/.venvs/cs239/bin/activate
pip install pyfhel