FC = gfortran
FFLAGS = -cpp -Wall -Wextra -O3


BUILD_DIR := ../build
LIB_DIR   := ../lib
VPATH = $(BUILD_DIR)

MODULE_SRC := tools.f90 benchmark_names.f90 benchmark_parameters.f90
# see https://www.gnu.org/software/make/manual/html_node/Text-Functions.html
MODULE_MOD := $(patsubst %.f90,$(BUILD_DIR)/%.mod,$(MODULE_SRC))
MODULE_O   := $(patsubst %.f90,$(BUILD_DIR)/%.o,$(MODULE_SRC)) $(BUILD_DIR)/benchmark_implementations.o $(BUILD_DIR)/benchmark_2D_CPU.o $(BUILD_DIR)/benchmark_2D_GPU.o

all: $(MODULE_MOD)
library: $(LIB_DIR)/library.a


$(BUILD_DIR)/%.o $(BUILD_DIR)/%.mod : %.f90 | $(BUILD_DIR)
	$(FC) $(FFLAGS) -c $< -o $(BUILD_DIR)/$(basename $<).o -J$(BUILD_DIR)

# according to https://www1.udel.edu/topics_css/software/special/language/fortran/fortran-docs/fortran-libraries1.html
# need this to override default modula2 compiling
$(BUILD_DIR)/benchmark_implementations.o $(BUILD_DIR)/benchmark_implementations.mod : benchmark_implementations.f90
	make -C .. build/benchmark_implementations.o
$(BUILD_DIR)/benchmark_2D_CPU.o $(BUILD_DIR)/benchmark_2D_CPU.mod : benchmark_2D_CPU.f90
	make -C .. build/benchmark_2D_CPU.o
$(BUILD_DIR)/benchmark_2D_GPU.o $(BUILD_DIR)/benchmark_2D_GPU.mod : benchmark_2D_GPU.f90
	make -C .. build/benchmark_2D_GPU.o

$(LIB_DIR)/library.a : $(MODULE_O) | $(LIB_DIR)
	ar cr $(LIB_DIR)/library.a $(MODULE_O)
	@touch $(LIB_DIR)/library.a


# DIRECTORIES
$(BUILD_DIR) $(LIB_DIR) :
	-@mkdir $@