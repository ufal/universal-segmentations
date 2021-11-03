curl --remote-name-all https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3247{/UDer-1.1.tgz}
tar -xzf UDer-1.1.tgz
cp UDer-1.1/la-WFL/UDer-1.1-la-WFL.tsv.gz .
gzip -d UDer-1.1-la-WFL.tsv.gz
rm UDer-1.1.tgz
rm -r UDer-1.1
echo "done"