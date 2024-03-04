echo ""
echo "######################################################################"
echo "###########################     TESTS      ###########################"
echo "###########################   RUNNIG LOX   ###########################"
echo "######################################################################"

count=1
for file in tests/*.lox; do
    echo ""
    echo "------------------------------------------------------------------------"
    echo "#$count- Running Lox file: $file"
    /usr/local/bin/python3 lox.py $file
    (( count++ ))
done
echo ""