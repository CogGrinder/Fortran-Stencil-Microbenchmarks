result(i,j) = 1.0_dp * array(i - 1, j - 1) &
    + 2.0_dp * array(i - 1, j + 1) &
    + 3.0_dp * array(i    , j    ) &
    + 4.0_dp * array(i + 1, j - 1) &
    + 5.0_dp * array(i + 1, j + 1)
result(i,j) = result(i,j)/15.0_dp