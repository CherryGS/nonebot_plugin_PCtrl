export RUN_TESTS=true && 
python -m pytest -s --cov=controller/ --cov-report=xml --db_choice=postgres