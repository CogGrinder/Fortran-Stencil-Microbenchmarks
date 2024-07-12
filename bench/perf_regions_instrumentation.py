#!/usr/bin/env python3


import sys
# here needs to be the proper folder for perf_regions
sys.path.append('src/perf_regions/scripts')

import perf_regions

pf = perf_regions.perf_regions(
        ["./","./src"],    # list with source directories
        [
            ".*timing_init.*",        # initialization of timing
            ".*timing_finalize.*",    # shutdown of timing

            ".*!pragma perf_regions include.*",    # include part

            ".*timing_start\(\'(.*)\'\)",    # start of timing
            ".*timing_stop\(\'(.*)\'\)",    # end of timing
            ".*timing_reset.*"        # reset of timing
        ],
#        '../../',    # perf region root directory
        './',        # output directory of perf region tools
        'fortran'
    )



if len(sys.argv) > 1:
    if sys.argv[1] == 'preprocess':
        print("PREPROCESS")
        pf.preprocessor()

    elif sys.argv[1] == 'cleanup':
        print("CLEANUP")
        pf.cleanup()

    else:
        print("Unsupported argument "+sys.argv[1])

else:
    pf.preprocessor()
