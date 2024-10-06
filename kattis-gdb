samplefile="$(pwd)/samples/$1.in"

if ! test -f $samplefile; then
    echo "Could not find test ($samplefile)"
    exit 1
fi

filename=$(pwd | awk 'BEGIN{FS="/"}{print $NF}').cpp
if [ $2 = "c" ]; then
    if ! test -f "./$filename"; then
        echo "Could not find file to compile"
        exit 1
    fi
    g++ -g $filename
fi
if ! test -f "./a.out"; then
    if ! test -f "./$filename"; then
        echo "Could not find executable or program to debug"
        exit 1
    fi
    g++ -g $filename
fi


gdb ./a.out -q -ex "start < '$samplefile'"
