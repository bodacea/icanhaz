
import xlrd
import xlwt

#set up
wbkin = xlrd.open_workbook(“infile.xls”)
wbkout = xlwt.Workbook()

#Read in data from Excel file
numsheets = wbkin.nsheets
sh=wbkin.sheet_by_index(0):
print(sh.nrows)
print(sh.ncols)
print(sh.cell_value(0,1))
merges = sh.mergedcells() 

#Print out contents of first worksheet
for r in range(0, sh.nrows):
    for c in range(0, sh.ncols):
        print("("+str(r)+","+str(c)+")"+str(sh.cell_value(r,c)))

#Write data out to Excel file
sheet = wbkout.add_sheet(“sheetname”, cell_overwrite_ok=True)
sheet.write(0,0, “cell contents”)
sheet.write(0,1, "more in the first row")
sheet.write(1,0, "contents in the second row")
wbkout.save(“outfile.xls”)
