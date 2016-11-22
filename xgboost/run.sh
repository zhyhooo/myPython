
config=$1
python -u train.py $config
python -u test.py $config
