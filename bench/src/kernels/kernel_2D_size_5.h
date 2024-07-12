! Bi-harmonic operator
! from https://www.researchgate.net/figure/Two-dimensional-stencils-for-the-Laplacian-operator-left-and-Bi-harmonic-operator_fig1_222563354
!        1      
!     2 -8  2   
!  1 -8 20 -8  1
!     2 -8  2   
!        1      
result(i,j) = 1.0_dp * array(i - 2, j) &
            + 2.0_dp * array(i - 1, j - 1) &
            - 8.0_dp * array(i - 1, j    ) &
            + 2.0_dp * array(i - 1, j + 1) &
            + 1.0_dp * array(i    , j - 2) &
            - 8.0_dp * array(i    , j - 1) &
            +20.0_dp * array(i    , j    ) &
            - 8.0_dp * array(i    , j + 1) &
            + 1.0_dp * array(i    , j + 2) &
            + 2.0_dp * array(i + 1, j - 1) &
            - 8.0_dp * array(i + 1, j    ) &
            + 2.0_dp * array(i + 1, j + 1) &
            + 1.0_dp * array(i + 2, j    )
result(i,j) = result(i,j)/15.0_dp