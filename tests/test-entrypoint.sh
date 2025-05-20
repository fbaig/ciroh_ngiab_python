#!/bin/bash
#/srv/conda/envs/notebook/bin/python /tests/tests.py -v 2>&1 | tee /tests/pyngiab_tests.log
#source /ngen/.venv/bin/activate && /srv/conda/envs/notebook/bin/python /tests/tests.py -v

# TEEHR(https://github.com/RTIInternational/teehr/) built-in tests
cd /tests && \
    git init teehr \
    && cd teehr \
    && git lfs install \
    && git remote add -f origin https://github.com/RTIInternational/teehr.git \
    && git config core.sparseCheckout true \
    && echo "tests/" >> .git/info/sparse-checkout \
    && git pull origin main
/srv/conda/envs/notebook/bin/pytest /tests/teehr/tests/ 2>&1 | tee /tests/teehr_tests.log
