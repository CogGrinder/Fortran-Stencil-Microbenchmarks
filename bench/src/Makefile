FC = gfortran
FFLAGS = -cpp -Wall -Wextra -O3


BUILD_DIR := ../build
LIB_DIR   := ../lib
VPATH = $(BUILD_DIR)

MODULE_SRC := $(wildcard *.f90)
# see https://www.gnu.org/software/make/manual/html_node/Text-Functions.html
MODULE_MOD := $(patsubst %.f90,$(BUILD_DIR)/%.mod,$(MODULE_SRC))
MODULE_O   := $(patsubst %.f90,%.o,$(MODULE_SRC))

all: $(MODULE_MOD) $(LIB_DIR)/library.a


$(BUILD_DIR)/%.mod : %.f90
	-$(FC) $(FFLAGS) -c $< -J$(BUILD_DIR) -I$(BUILD_DIR)

$(BUILD_DIR)/benchmark_implementations.mod : $(BUILD_DIR)/benchmark_names.mod
# %.o : %.f90
# 	-$(FC) $(FFLAGS) -c $< -J$(BUILD_DIR) -I$(BUILD_DIR)

# according to https://www1.udel.edu/topics_css/software/special/language/fortran/fortran-docs/fortran-libraries1.html
# need this to override default modula2 compiling
%.o : %.mod
$(LIB_DIR)/library.a : $(MODULE_O)
	ar cr $(LIB_DIR)/library.a $(MODULE_O)
