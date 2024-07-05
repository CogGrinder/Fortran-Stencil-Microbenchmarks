! x derivation
! with (i,j) as (y,x)
result(i,j) = 2.0_dp * array(i    , j - 1) &
            - 4.0_dp * array(i    , j    ) &
            + 2.0_dp * array(i    , j + 1)
result(i,j) = result(i,j)/2.0_dp