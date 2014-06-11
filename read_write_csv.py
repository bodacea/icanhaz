import csv

#Set up 
fin = open(“infile.csv”, “rb”)
fout = open(“outfile.csv”, “wb”)
csvin = csv.reader(fin)
csvout = csv.writer(fout, quoting=csv.QUOTE_NONNUMERIC)  

#Read in header row
headers = csvin.next()


for header in headers:
    print(header)


#Read in non-header rows 
for row in csvin:
    for col in range(0,len(row)):
        print(row[col])

#Write out
csvout.writerow([“header1”, “header2”, “header3”])
for row in csvin:
    csvout.writerow(row)

#tidy up
fin.close()
fout.close()
