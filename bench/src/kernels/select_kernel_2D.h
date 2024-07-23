#if   KERNEL_MODE == DEFAULT_KERNEL
# include "kernels/kernel_2D_default.h"
#elif KERNEL_MODE == X_KERNEL
# include "kernels/kernel_2D_x.h"
#elif KERNEL_MODE == Y_KERNEL
# include "kernels/kernel_2D_y.h"
#elif KERNEL_MODE == SIZE_5_KERNEL
# include "kernels/kernel_2D_size_5.h"
#else
# include "kernels/kernel_2D_default.h"
#endif /*KERNEL_MODE*/