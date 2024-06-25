FC = gfortran
FFLAGS = -cpp -O3 # -Wall -Wextra


BIN_DIR := ../bin
BUILD_DIR := ../build
LIB_DIR   := ../lib
VPATH = $(BUILD_DIR)

MODULE_SRC := tools.f90 benchmark_names.f90 benchmark_parameters.f90
# see https://www.gnu.org/software/make/manual/html_node/Text-Functions.html
MODULE_MOD := $(patsubst %.f90,$(BUILD_DIR)/%.mod,$(MODULE_SRC))
MODULE_O   := $(patsubst %.f90,$(BUILD_DIR)/%.o,$(MODULE_SRC)) $(BUILD_DIR)/benchmark_implementations.o $(BUILD_DIR)/benchmark_2D_CPU.o $(BUILD_DIR)/benchmark_2D_GPU.o

all: $(MODULE_MOD)
library: $(LIB_DIR)/library.a

# default rule
$(BUILD_DIR)/%.o $(BUILD_DIR)/%.mod : %.f90 | $(BUILD_DIR)
	$(FC) $(FFLAGS) -c $< -o $(BUILD_DIR)/$(basename $<).o -J$(BUILD_DIR)

# according to https://www1.udel.edu/topics_css/software/special/language/fortran/fortran-docs/fortran-libraries1.html
# need this to override default modula2 compiling

####################### compilation flags ########################
BENCH_LIB := -L$(LIB_DIR) -l:library.a
# TODO : try .so library - you must also modify the Makefile in src
# BENCH_LIB := -L$(LIB_DIR) -l:library.so
# TODO : try not using .a or .so
# BENCH_LIB := -L$(LIB_DIR)

PAPI_LIB:=-L. -lpapi

# set PERF_REGIONS_FOLDER, default is in the folder next to bench
PERF_REGIONS_FOLDER:=../../perf_regions

PERFREGION_LIB:=-L$(PERF_REGIONS_FOLDER)/build -lperf_regions -I$(PERF_REGIONS_FOLDER)/build
PERFREGION_SRC:=$(PERF_REGIONS_FOLDER)/src

CFLAGS:= -I$(BUILD_DIR) -I$(PERFREGION_SRC)
PERFREGION_LINKFLAGS:= ${PAPI_LIB} ${PERFREGION_LIB}


$(BUILD_DIR)/benchmark_implementations.o : $(BUILD_DIR)/benchmark_implementations.mod
	@touch $(BUILD_DIR)/benchmark_implementations.o
$(BUILD_DIR)/benchmark_implementations.mod : benchmark_implementations.f90
# ./perf_regions_instrumentation.py cleanup
	${FC} ${FFLAGS} -c benchmark_implementations.f90 -o $(BUILD_DIR)/benchmark_implementations.o ${CFLAGS} ${PERFREGION_LINKFLAGS} -L$(LIB_DIR) -J$(BUILD_DIR)

$(BUILD_DIR)/benchmark_2D_CPU.o : $(BUILD_DIR)/benchmark_2D_CPU.mod
	@touch $(BUILD_DIR)/benchmark_2D_CPU.o
$(BUILD_DIR)/benchmark_2D_CPU.mod : benchmark_2D_CPU.f90
# ./perf_regions_instrumentation.py cleanup
	${FC} ${FFLAGS} -c benchmark_2D_CPU.f90 -o $(BUILD_DIR)/benchmark_2D_CPU.o ${CFLAGS} ${PERFREGION_LINKFLAGS} -L$(LIB_DIR) -J$(BUILD_DIR)


$(BUILD_DIR)/benchmark_2D_GPU.o : $(BUILD_DIR)/benchmark_2D_GPU.mod
	@touch $(BUILD_DIR)/benchmark_2D_GPU.o
$(BUILD_DIR)/benchmark_2D_GPU.mod : benchmark_2D_GPU.f90
# ./perf_regions_instrumentation.py cleanup
	${FC} ${FFLAGS} -c benchmark_2D_GPU.f90 -o $(BUILD_DIR)/benchmark_2D_GPU.o ${CFLAGS} ${PERFREGION_LINKFLAGS} -L$(LIB_DIR) -J$(BUILD_DIR)



# $(BUILD_DIR)/benchmark_implementations.o $(BUILD_DIR)/benchmark_implementations.mod : benchmark_implementations.f90
# 	make -C .. build/benchmark_implementations.o
# $(BUILD_DIR)/benchmark_2D_CPU.o $(BUILD_DIR)/benchmark_2D_CPU.mod : benchmark_2D_CPU.f90
# 	make -C .. build/benchmark_2D_CPU.o
# $(BUILD_DIR)/benchmark_2D_GPU.o $(BUILD_DIR)/benchmark_2D_GPU.mod : benchmark_2D_GPU.f90
# 	make -C .. build/benchmark_2D_GPU.o

$(LIB_DIR)/library.a : $(MODULE_O) | $(LIB_DIR)
	ar cr $(LIB_DIR)/library.a $(MODULE_O)
	@touch $(LIB_DIR)/library.a



# DIRECTORIES
$(BUILD_DIR) $(LIB_DIR) :
	-@mkdir $@