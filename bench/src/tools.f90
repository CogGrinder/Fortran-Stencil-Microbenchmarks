MODULE tools
    integer, parameter :: dp=kind(0.d0)
    contains
        SUBROUTINE stencil_characteristics(stencil, sum, length)
            integer, dimension(:), intent(in) :: stencil
            real, intent(out)    :: sum
            integer, intent(out) :: length
            length = size(stencil)
            sum = 0.0_dp
            do i = 1, length
                sum = sum + stencil(i)
            end do
        END SUBROUTINE stencil_characteristics
        SUBROUTINE stencil_characteristics_2D(stencil, sum, length)
            integer, dimension(:,:), intent(in) :: stencil
            real, intent(out)    :: sum
            integer, intent(out) :: length
            length = size(stencil,dim=1)
            sum = 0.0_dp
            do j = 1, length
                do i = 1, length
                    sum = sum + stencil(i,j)
                end do
            end do
        END SUBROUTINE stencil_characteristics_2D
        SUBROUTINE stencil_characteristics_3D(stencil, sum, length)
            integer, dimension(:,:,:), intent(in) :: stencil
            real, intent(out)    :: sum
            integer, intent(out) :: length
            length = size(stencil,dim=1)
            sum = 0.0_dp
            do k = 1, length
                do j = 1, length
                    do i = 1, length
                        sum = sum + stencil(i,j,k)
                    end do
                end do
            end do
        END SUBROUTINE stencil_characteristics_3D
end MODULE