#!/usr/bin/env python

csvFile = input('please input csv file:')
vcfTemp = input('please input the place you want to store vcf file.e.g /path/to/filename.vcf:')
vcfFile = open(vcfTemp,'w')
t = open(csvFile,'r')
csvTitle = t.readline().split(',')
vcfTitle = []
n = 0
for i in csvTitle:
    vcfTitle.append(input('please input {} convert to[tel,address,name],enter to ignore:'.format(csvTitle[n])))
    n = n + 1

t.seek(0)
counts = len(t.readlines())
t.seek(1)
f = 0
while f != counts:
    csvls = t.readline().split(',')
    #print(csvls)
    vcfFile.write('BEGIN:VCARD'+'\n')
    vcfFile.write('VERSION:3.0'+'\n')
    for i in vcfTitle:
        if i =='':
            pass
        elif i.upper()=='TEL':
            vcfFile.write('TEL;CELL'+':'+csvls[vcfTitle.index(i)]+'\n')
        elif i.upper()=='ADDRESS':
            vcfFile.write('ADR'+':'+csvls[vcfTitle.index(i)]+'\n')
        elif i.upper()=='NAME':
            vcfFile.write('FN'+':'+csvls[vcfTitle.index(i)]+'\n')
    vcfFile.write('END:VCARD'+'\n')
    f = f + 1
t.close()
vcfFile.close()
