import csv
import random
# names of files to read from
r_filenameCSV = './test.csv'

# data structures to hold the data
csv_labels = []
csv_data = []

# read the data
with open(r_filenameCSV, 'r') as csv_in:
    csv_reader = csv.reader(csv_in)

    # read the first line that holds column labels
    csv_labels = csv_reader.__next__()
   
    # iterate through all the records
    for record in csv_reader:
        csv_data.append(record)

# print (csv_data[0][0])
# random.shuffle(csv_data)


with open('./dev.tsv', 'wt') as out_file:
    tsv_writer = csv.writer(out_file, delimiter='\t')
    tsv_writer.writerow(['sentence', 'label'])
    for i in csv_data:
        tsv_writer.writerow([i[0], "0"])