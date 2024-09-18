This library is designed to work on Linux with PAPI, and does not currently support Windows. WSL may be functional but is not supported.
# Installation steps
## Python requirements
- process ``requirements.txt`` in the root folder of the project:
```bash
$ pip install -r requirements.txt
```
This will install numpy and matplotlib in your current python environment.
sudo may be necessary depending on your python environment.

## Other requirements
For nvfortran and GPU benchmarks, one must configure exports TODO: explain export handling once done


## For performance counters ``perf_regions`` dependency
- [sudo] For quick activation of papi, temporarily add access to performance events with this line:  
```bash
$ sudo bash -c 'echo "-1" > /proc/sys/kernel/perf_event_paranoid'

If this does not work install a papi-tools package.
To compile using papi, you will need a libpapi-dev package.

- [sudo] If you need to activate performance events access permanently, contact your administrator add the line:
```json
kernel.perf_event_paranoid = -1
```
in ```/etc/sysctl.conf```. It gives this access to all users of the machine.

### Fix for missing performance counters
- To detail which events are available, run this line:
```bash
$ papi_avail
```
- Depending on your available events, you may have to change the line ``export PERF_REGIONS_COUNTERS="PAPI_L1_TCM,PAPI_L2_TCM,PAPI_L3_TCM,WALLCLOCKTIME"`` of [``codegen.py``](../bench/preprocess/codegen.py) to generate benchmarks that only track ``WALLCLOCKTIME`` for instance. In most HPC systems you may ignore this step.
- Modify the line ``all_data_values=['PAPI_L1_TCM',  'PAPI_L2_TCM',  'PAPI_L3_TCM',  'WALLCLOCKTIME']`` in [``generate_graph.py``](../bench/postprocess/generate_graph.py) in the same way for values to match.
TODO: config file to do this without editing source