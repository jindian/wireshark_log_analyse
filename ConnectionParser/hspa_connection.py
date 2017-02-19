#!/usr/bin/python

import sys
import os
import csv
import string

class hspa_connection:
    def __init__(self, dir):
        self.dir = dir
        self.file_list = os.listdir(self.dir)
        self.hsdpa_file_list = []
        self.header_dictionary = {}

        for file in self.file_list:
            file_len = len(file)
            if (file.find("type2", 0, file_len) is not -1) or (file.find("type1", 0, file_len) is not -1):
                self.hsdpa_file_list.append(file)

        self.generate_header_directory()

    def generate_header_directory(self):
        if len(self.hsdpa_file_list) is 0:
            print "No HSDPA connections found"
            return

        file_dir = self.dir + '/' + self.hsdpa_file_list[0]
        with open(file_dir, 'rb') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', quotechar='|')
            for row in csv_reader:
                line = ','.join(row)
                column = line.split(',')
                cell_index = 0
                for cell in column:
                    self.header_dictionary[cell] = cell_index
                    cell_index += 1

                return


    def get_hsfach_connections(self):
        fi_index = self.header_dictionary.get("fi")
        for file in self.hsdpa_file_list:
            file_dir = self.dir + '/' + file
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
        print "Input parameter not enough!!\n\r"
        sys.exit(1)

    args = sys.argv
    hspa_conn_instance = hspa_connection(args[1])
    hspa_conn_instance.get_hsfach_connections()
