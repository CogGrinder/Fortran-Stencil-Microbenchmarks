! y derivation
! with (i,j) as (y,x)
result(i,j) = 2.0_dp * array(i - 1, j    ) &
            - 4.0_dp * array(i    , j    ) &
            + 2.0_dp * array(i + 1, j    )
result(i,j) = result(i,j)/8.0_dp