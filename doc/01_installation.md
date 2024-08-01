This library is designed to work on Linux with PAPI, and does not currently support Windows. WSL may be functional but is not supported.
# Installation steps
## Python requirements
- process ``requirements.txt``
```bash
$ pip install -r requirements.txt
```
warning: will install numpy and matplotlib in your current python environment

## Other requirements
For nvfortran and GPU benchmarks, one must configure exports TODO: explain export handling once done

## For performance counters ``perf_regions`` dependency
- [sudo] For quick activation of papi, temporarily add access to performance events with this line:  
```bash
$ sudo bash -c 'echo \"-1\" > /proc/sys/kernel/perf_event_paranoid'
```
- [sudo] If you need to activate performance events access permanently, contact your administrator add the line:
```json
kernel.perf_event_paranoid = -1
```
in ```/etc/sysctl.conf```. It gives this access to all users of the machine.

- To detail which events are available, run this line:
```bash
$ papi_avail
```
depending on your available events, you may have to change the line ``export PERF_REGIONS_COUNTERS="PAPI_L1_TCM,PAPI_L2_TCM,PAPI_L3_TCM,WALLCLOCKTIME"`` of [``codegen.py``](../bench/preprocess/codegen.py) to generate benchmarks that only track ``WALLCLOCKTIME`` for instance. In most HPC systems you may ignore this step.