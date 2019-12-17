import csv
import random
# names of files to read from
r_filenameCSV = '/home/alex/Data_Science/HW4/0510727/utils/glue_data/SST-2/train.csv'
# r_filenameTSV = '../../Data/Chapter01/realEstate_trans.tsv'

# data structures to hold the data
csv_labels = []
tsv_labels = []
csv_data = []
tsv_data = []

# read the data
with open(r_filenameCSV, 'r') as csv_in:
    csv_reader = csv.reader(csv_in)

    # read the first line that holds column labels
    csv_labels = csv_reader.__next__()
   
    # iterate through all the records
    for record in csv_reader:
        csv_data.append(record)

# print (csv_data[0][0])
random.shuffle(csv_data)

with open('/home/alex/Data_Science/HW4/0510727/utils/glue_data/SST-2/train.tsv', 'wt') as out_file:
    tsv_writer = csv.writer(out_file, delimiter='\t')
    tsv_writer.writerow(['sentence', 'label'])
    for i in csv_data[:-2000]:
        tsv_writer.writerow([i[0], i[2]])

