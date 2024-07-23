# thank you to https://aoterodelaroza.github.io/devnotes/modern-fortran-makefiles/
# to debug preprocessor, use cpp -E benchmark_2d_cpu.F90 -DSIZE_AT_COMPILATION=1 -DNI=1024 -DNJ=1024 -Iperf_regions/src
# see https://www.gnu.org/software/make/manual/html_node/Chained-Rules.html for special targets
.SUFFIXES: #disable automatic rules to override default modula2 compiling
# (avoid .mod being interpreted as modula-2 source files)
F90?=gfortran
NV = nvfortran
FFLAGS = -cpp -O3 #-Wall -Wextra


BIN_DIR := ../bin
BUILD_DIR := ../build
LIB_DIR   := ../lib
SRC_DIR   := .
VPATH = $(BUILD_DIR)


MODULE_F90 := $(wildcard $(SRC_DIR)/*.F90)

# # if not compiling with nvfortran, ignore benchmark_2d_gpu.F90
# ifneq ( $(F90) , nvfortran )
# MODULE_F90 := $(MODULE_F90:$(SRC_DIR)/benchmark_2d_gpu.F90=)
# endif

# see https://www.gnu.org/software/make/manual/html_node/Text-Functions.html
MODULE_O := $(patsubst $(SRC_DIR)/%.F90,$(BUILD_DIR)/%.o, $(MODULE_F90))

####################### defaults #######################

ifndef DIM
export DIM=2
endif

ifndef ALLOC_MODE
export ALLOC_MODE=DEFAULT_ALLOC
endif

ifndef MODULE_MODE
export MODULE_MODE=0
endif

ifndef SIZE_MODE
export SIZE_MODE=NONE
endif

ifndef SIZE_AT_COMPILATION
export SIZE_AT_COMPILATION=0
endif

ifndef KERNEL_MODE
export KERNEL_MODE=DEFAULT_KERNEL
endif

####################### targets #######################

all: $(MODULE_O)
library: $(LIB_DIR)/libbench.a

####################### compilation flags ########################
BENCH_LIB := -L$(LIB_DIR) -lbench
PAPI_LIB:=-L. -lpapi

# set PERF_REGIONS_FOLDER, default is in the folder next to bench
ifdef _PERF_REGIONS_FOLDER
PERF_REGIONS_FOLDER=../$(_PERF_REGIONS_FOLDER)
else
PERF_REGIONS_FOLDER:=perf_regions
endif

PERFREGION_LIB:=-L$(PERF_REGIONS_FOLDER)/build -lperf_regions -I$(PERF_REGIONS_FOLDER)/build
PERFREGION_SRC:=$(PERF_REGIONS_FOLDER)/src

CPPMACROS:=-DDIM=${DIM} -DALLOC_MODE=${ALLOC_MODE} -DMODULE_MODE=${MODULE_MODE} -DSIZE_MODE=${SIZE_MODE} -DSIZE_AT_COMPILATION=${SIZE_AT_COMPILATION} -DKERNEL_MODE=${KERNEL_MODE} -DNI=${NI} -DNJ=${NJ}
CFLAGS:= $(CPPMACROS) -I$(BUILD_DIR) -I$(SRC_DIR) -I$(PERFREGION_SRC)
PERFREGION_LINKFLAGS:= ${PAPI_LIB} ${PERFREGION_LIB}

####################### extra dependency rules #######################

$(BUILD_DIR)/benchmark_parameters.o : $(BUILD_DIR)/benchmark_names.mod
$(BUILD_DIR)/benchmark_1d.o : $(BUILD_DIR)/tools.mod $(BUILD_DIR)/benchmark_names.mod
$(BUILD_DIR)/benchmark_2d_cpu.o : $(BUILD_DIR)/tools.mod $(BUILD_DIR)/benchmark_parameters.mod
$(BUILD_DIR)/benchmark_2d_gpu.o : $(BUILD_DIR)/tools.mod $(BUILD_DIR)/benchmark_parameters.mod

####################### compilation of modules #######################

# default rule
$(BUILD_DIR)/%.o $(BUILD_DIR)/%.mod : $(SRC_DIR)/%.F90 | $(BUILD_DIR)
	$(F90) $(FFLAGS) -c $< -o $(BUILD_DIR)/$(basename $<).o $(CFLAGS)
	@mv -f $(<:.F90=.mod) "${BUILD_DIR}"

$(BUILD_DIR)/benchmark_1d.o $(BUILD_DIR)/benchmark_1d.mod : $(SRC_DIR)/benchmark_1d.F90 | $(BUILD_DIR)
	${F90} ${FFLAGS} -c $< -o $(BUILD_DIR)/benchmark_1d.o ${CFLAGS} ${PERFREGION_LINKFLAGS} -L$(LIB_DIR)
	@mv -f $(<:.F90=.mod) "${BUILD_DIR}"

$(BUILD_DIR)/benchmark_2d_cpu.o $(BUILD_DIR)/benchmark_2d_cpu.mod : $(SRC_DIR)/benchmark_2d_cpu.F90 | $(BUILD_DIR)
	${F90} ${FFLAGS} -c $< -o $(BUILD_DIR)/benchmark_2d_cpu.o ${CFLAGS} ${PERFREGION_LINKFLAGS} -L$(LIB_DIR)
	@mv -f $(<:.F90=.mod) "${BUILD_DIR}"

# GPU compilation commented when FC is not nvfortran:
$(BUILD_DIR)/benchmark_2d_gpu.o $(BUILD_DIR)/benchmark_2d_gpu.mod : $(SRC_DIR)/benchmark_2d_gpu.F90 | $(BUILD_DIR)
ifeq ( $(F90) , nvfortran )
	${NV} -cpp -Minfo=mp -mp=gpu -gpu=sm_75 $< -o $(BUILD_DIR)/benchmark_2d_gpu.o ${CFLAGS} ${PERFREGION_LINKFLAGS} -L$(LIB_DIR)
	@mv -f $(<:.F90=.mod) "${BUILD_DIR}"
else
	${F90} ${FFLAGS} -c $< -o $(BUILD_DIR)/benchmark_2d_gpu.o -DNO_GPU ${CFLAGS} ${PERFREGION_LINKFLAGS} -L$(LIB_DIR)
	@mv -f $(<:.F90=.mod) "${BUILD_DIR}"
endif

# please note: timestamp resolution in archives is lower according to
# documentation of make's .LOW_RESOLUTION_TIME at
# https://www.gnu.org/software/make/manual/html_node/Special-Targets.html
$(LIB_DIR)/libbench.a : $(MODULE_O) | $(LIB_DIR)
	ar crUuv $(LIB_DIR)/libbench.a $?


# DIRECTORIES
$(BUILD_DIR) $(LIB_DIR) :
	-@mkdir $@