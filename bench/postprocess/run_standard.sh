cd ~/Fortran-Stencil-Microbenchmarks/bench/postprocess
folder_name=all_benchmarks_07_31
mkdir -p $folder_name
make -C .. clean --silent
cd ../preprocess
# TODO: --module True set because non-module not yet implemented and graphing can break
## Basic bench:
python3 codegen.py -c --module True --size 1 -A 1 --compile-size False --compile-loop-bound True --hardware CPU

## Full bench:
# python3 codegen.py -c --module True --size-range 2048 1024 512 128 -A 5
./run_bench_tree.sh #-vcompile #-vout #-vompgpu
cd ../postprocess
./collect_data_csv.sh -nv

## Basic bench:
python3 generate_graph.py -sp -D $folder_name/graphs -G all -sG all

## Full bench:
# python3 generate_graph.py -sp -D $folder_name/graphs -G all -sG all