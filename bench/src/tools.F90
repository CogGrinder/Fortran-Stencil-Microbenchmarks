MODULE TOOLS
    ! TODO : WARNING : hard coded type
    integer, parameter :: dp=kind(0.d0)
    contains
        
        SUBROUTINE get_key_value(arg, value)
            character(len=*), intent(in) :: arg
            integer, intent(out) :: value
            integer :: pos
        
            ! Find the '='
            pos = index(arg, '=')
            if (0 < pos .and. pos < len(arg)) then
                read(arg(pos+1:),*) value
            end if
        end SUBROUTINE get_key_value
        SUBROUTINE ANTI_OPTIMISATION_WRITE(written)
            implicit none
            real(kind=dp), intent(in) :: written
            integer :: id = 42
            character(len=42) :: filename
            
            filename = 'tmp.txt'
        
            open(unit=id, file=filename, status='unknown')
            write(id,*) written
            close(id)
        end SUBROUTINE ANTI_OPTIMISATION_WRITE
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