MODULE benchmark_implementations
    use benchmark_names
    implicit none
    
    contains
        SUBROUTINE TEST_COMPUTATION_0()
        end SUBROUTINE
        SUBROUTINE TEST_COMPUTATION_1()
        end SUBROUTINE

end MODULE


SUBROUTINE TEST_COMPUTATION_0()
! ! TODO
!     do i = 1, ARRAY_LEN-sten_len+1
!         result(i + sten_len/2) = 0
!         do j = 1,sten_len
! #ifdef DEBUG
!         write(6, 1, advance="no") j, i-sten_len/2 + j
! #endif
!             ! TODO : is there a += operator ?
!             result(i + sten_len/2) = result(i + sten_len/2) + stencil(j) * array(i-sten_len/2 + j)
!         end do
! #ifdef DEBUG        
!     write(*,*) " at index " , i + sten_len/2
! #endif
!     end do
!     ! we ignore edges in the computation which explains the shift in indexes

!     ! normalize by sten_sum
!     do i = 1, ARRAY_LEN
!         result(i) = result(i)/sten_sum
!     end do
end SUBROUTINE
SUBROUTINE TEST_COMPUTATION_1()
end SUBROUTINE