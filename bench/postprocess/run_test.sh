cd ~/Fortran-Stencil-Microbenchmarks/bench/postprocess
mkdir -p gpu_cpu_bench_test
make -C .. clean --silent
for size in 128 512 1024 2048
do
    cd ../preprocess
    # TODO: --module True set because non-module not yet implemented and graphing can break
    python3 codegen.py --size $size --kernel-mode DEFAULT_KERNEL -c -nv --module True
    ./run_bench_tree.sh #-vompgpu
    cd ../postprocess
    ./collect_data_csv.sh -nv
    python3 generate_graph.py -D gpu_cpu_bench_test/gpu_cpu_$(printf $size)Mb -sp -G hardware -sG all
done