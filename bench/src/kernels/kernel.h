#if KERNEL_MODE == NO_INCLUDE
            result(i,j) = 1.0_dp * array(i - 1, j - 1) &
                        + 2.0_dp * array(i - 1, j + 1) &
                        + 3.0_dp * array(i    , j    ) &
                        + 4.0_dp * array(i + 1, j - 1) &
                        + 5.0_dp * array(i + 1, j + 1)
            result(i,j) = result(i,j)/15.0_dp
#else
# if   KERNEL_MODE == DEFAULT_KERNEL
#  include "kernels/kernel_2D_default.h"
# elif KERNEL_MODE == X_KERNEL
#  include "kernels/kernel_2D_x.h"
# elif KERNEL_MODE == Y_KERNEL
#  include "kernels/kernel_2D_y.h"
# elif KERNEL_MODE == SIZE_5_KERNEL
#  include "kernels/kernel_2D_size_5.h"
# else
#  include "kernels/kernel_2D_default.h"
# endif /*KERNEL_MODE*/
#endif /*NO_INCLUDE*/