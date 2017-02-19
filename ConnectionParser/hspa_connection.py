#!/usr/bin/python

import sys
import os
import csv

fi_index = 22


def get_fi(dir):
    file_list = os.listdir(dir)
    for file in file_list:
        if file != 'Hsdsch_per_connect_stat.csv' and file != 'Hsdsch_per_second_stat.csv':
            file_dir = dir + '/' + file
            with open(file_dir, 'rb') as csv_file:
                line_no = 0
                csv_reader = csv.reader(csv_file, delimiter=',', quotechar='|')
                for row in csv_reader:
                    if line_no is 0:
                        line_no += 1
                        continue

                    if row[fi_index] is '1':
                        print file
                        break
                    else:
                        if row[fi_index] is '0':
                            break

                    line_no += 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Input parameter not enough!!\n"

    args = sys.argv
    get_fi(args[1])
