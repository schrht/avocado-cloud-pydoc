# avocado-cloud-pydoc

## Parsing pydoc

### Json for Polarion Updates

The `dump_testcases.py` is used to parse the pydoc for Polarion usage.

```bash
# Parse Aliyun testcases for polarion to import.
dump_testcases.py --product Aliyun --pypath ./avocado-cloud/tests/alibaba \
                  --output-format json-polarion --output testcases.json

# Parse AWS testcases for polarion to import.
dump_testcases.py --product AWS --pypath ./avocado-cloud/tests/aws \
                  --output-format json-polarion --output testcases.json
```

Then you can load `testcases.json` into Polarion by [this script](https://gitlab.cee.redhat.com/3rd/3rd-tools/-/blob/master/tools/polarion_avocado_case_add.py).

Or you can use the all-in-one CI job directly.

> All-in-one CI job:
> https://ci-jenkins-csb-esxi.apps.ocp4.prod.psi.redhat.com/view/Tools/job/AWS-Aliyun-polarion-update/
