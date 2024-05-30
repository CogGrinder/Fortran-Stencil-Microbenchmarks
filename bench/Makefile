### bench makefile ###

FC:=gfortran

all: build_bench
run: run_main
clean: clean_bench

MAIN:= main

# add .exe to executable name if Windows
ifeq ($(OS),Windows_NT)
MAIN:= $(MAIN).exe
endif

EXECS := $(MAIN) # add new executables here





PAPI_LIB:=-L. -lpapi

# set PERF_REGIONS_FOLDER, default is in the folder next to 
PERF_REGIONS_FOLDER:=../perf_regions
ifdef PERF_REGIONS
	PERF_REGIONS_FOLDER = $(PERF_REGIONS)
endif

PERFREGION_LIB:=-L$(PERF_REGIONS_FOLDER)/build -lperf_regions -I$(PERF_REGIONS_FOLDER)/build
PERFREGION_SRC:=$(PERF_REGIONS_FOLDER)/src
CFLAGS_PERFREGION:=-I$(PERFREGION_SRC)
LINKFLAGS_PERFREGION:=${PAPI_LIB} ${PERFREGION_LIB}


build_bench:
	make -C $(PERFREGION_SRC)
	make $(MAIN)

$(MAIN) : main.f90
# TODO : ./instrumentation.py cleanup
# ./instrumentation.py preprocess
	${FC} -g -o $(MAIN) main.f90 -cpp ${CFLAGS_PERFREGION} ${LINKFLAGS_PERFREGION}
# TODO : put back -cpp option does preprocessing

run_main : build_bench
# TODO : here replace by a ./run_benches.sh
	./$(MAIN)

#main.o:
#	${FC} -c main.F90 ${CFLAGS_PERFREGION} ${LINKFLAGS_PERFREGION}


# clean depending on OS
ifeq ($(OS),Windows_NT)
clean_bench:
	rm *.exe
	rm *.o
else
clean_bench:
# ./instrumentation.py cleanup
	rm -f main main_perf_region main.o
	rm -f perf_region_list.txt
endif