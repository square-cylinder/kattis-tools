rm samples.zip 2> /dev/null
rm -r samples 2> /dev/null
url="https://open.kattis.com/problems/$1/file/statement/samples.zip"
if wget -nv $url 1> /dev/null; then
    unzip samples.zip -d samples > /dev/null
    rm samples.zip
else
    echo "could not resolve problem ($url)"
fi
