progress() {
n=$(( 24 * $1 / 100 ))
progresspercent=$(printf "%3d" $((100 * $1/100)))
progressbar=$(printf -- '-%.0s' $(seq 1 $n))$(printf ' %.0s' $(seq $n 24))
echo -ne "$progressbar ($progresspercent%)\r"
}

# echo -ne '#####                     (33%)\r'
progress 33
sleep 1
echo -ne '                                \r'
echo bla
echo ble
echo bli
echo blo
echo blu
progress 66
sleep 1
echo -ne '                                \r'
# echo -ne 'bla\r'
# echo
echo 'bla'
echo ble
echo bli
echo blo
echo blu
progress 100
# echo -ne '#######################   (100%)\r'
echo -ne '\n'
echo seq 16 15 $(seq 16 15)
echo seq 16 1 15 $(seq 16 1 15)
echo seq 16 -1 15 $(seq 16 -1 15)