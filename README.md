# avocado-cloud-pydoc

## Parsing pydoc

The `dump_testcases.py` is used to parse the pydoc for testcases.

Usage:
```
# Parse Aliyun testcases for polarion to import.
dump_testcases.py --product Aliyun --pypath ./avocado-cloud/tests/alibaba \
                  --output-format json-polarion --output testcases.json

# Parse AWS testcases for polarion to import.
dump_testcases.py --product AWS --pypath ./avocado-cloud/tests/aws \
                  --output-format json-polarion --output testcases.json
```
