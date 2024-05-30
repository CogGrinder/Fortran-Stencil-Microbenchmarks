### bench makefile ###

all: bench
run: run_all_bench
clean: clean_bench

MAIN:= main

# add .exe to executable name if Windows
ifeq ($(OS),Windows_NT)
MAIN:= $(MAIN).exe
endif

EXECS := $(MAIN)

bench: $(EXECS)

$(MAIN) : main.f90
	gfortran main.f90 -o $(MAIN)

run_all_bench: run_main
run_main : $(MAIN)
	./$(MAIN)


# clean depending on OS
ifeq ($(OS),Windows_NT)
clean_bench:
	rm *.exe
else
clean_bench:
# grep version
# note 1 : grep -v "\." removes from ls all files containing a dot
#          indeed, "." is a metacharacter ie regex for one character
# note 2 : xargs removes each file
#          if doing to subdirectory, use $$ xargs -I file rm $(SUBDIR)/file
	ls | grep -v "\." | grep -v Makefile | xargs rm
# TODO : simpler $$ find version
endif