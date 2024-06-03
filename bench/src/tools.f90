MODULE tools
    contains
        SUBROUTINE stencil_characteristics(stencil, sum, length)
            integer, dimension(:), intent(in) :: stencil
            integer, intent(out) :: sum, length
            length = size(stencil)
            sum = 0
            do i = 1, length
                sum = sum + stencil(i)
            end do
        END SUBROUTINE stencil_characteristics
end MODULE