exec="$1"
filetocopy="$1"
if [[ "$1" =~ .*\.cpp ]]; then
    echo "compiling..."
    if ! g++ "$1" -g; then
        echo "compilation failed!"
        exit 1
    fi
    exec="./a.out"
elif [[ "$1" =~ .*\.py ]]; then
    exec="python3 $1"
else
    echo "please provide a valid file to test, supported files are .cpp, .py"
    exit 1
fi

samplenames=$(find ./samples/ -name '*.in' | awk 'BEGIN{FS="[/.]"}{print $(NF-1)}')

allpassed=true
for name in $samplenames; do
    echo "running $name"
    output=$($exec < ./samples/$name.in)
    if [ ! $? ]; then
        echo "Testcase failed... ($name)"
        echo "program returned with bad exit code:"
        echo "$output"
        allpassed=false
        break
    fi
    if [ "$output" != "$(cat ./samples/$name.ans)" ]; then
        echo "Testcase failed... ($name)"
        echo "Your output:"
        echo "$output"
        echo "Expected:"
        cat ./samples/$name.ans
        allpassed=false
        break
    fi
    echo "Testcase \"$name\" passed!"
done

if [ $allpassed = true ]; then
    echo "All testcases passed! "
    echo "Do you want to copy the source code to the system clipboard ($(wc -c $filetocopy | cut -d" " -f1) bytes)? (y/n)"
    read answer
    if [[ "$answer" =~ [Yy] ]]; then
        cat $filetocopy | xclip -selection clipboard
        echo "Code stored in clipboard."
    fi
fi
