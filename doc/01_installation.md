# Installation steps
- python requirements
    - process ``requirements.txt``
    ```bash
    $ pip install -r requirements.txt
    ```
    warning: will install numpy and matplotlib in your current python environment

- for performance counters ``perf_regions`` dependency
    - Check for availability of events:
    ```bash
    $ papi_avail
    ```
    if not, change ``codegen_bench_tree_branch`` of [``codegen.py``](../bench/preprocess/codegen.py) to generate bench that only tracks ``WALLCLOCKTIME`` - TODO: currently does not support use of systems which have no access to PAPI eg, Windows
    - In case that performance events are not available, contact your administrator add the line:
    ```json
    kernel.perf_event_paranoid = -1
    ```
    in ```/etc/sysctl.conf```
    or temporarily set this with the command
    ```bash
    $ sudo bash -c 'echo \"-1\" > /proc/sys/kernel/perf_event_paranoid'
    ```