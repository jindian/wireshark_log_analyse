#!/usr/bin/python

import sys
import os
import csv

"""
Class:
            hspa_connection
Usage:
            Manager all udp connections
Interfaces:
            get_file_list               : get all udp connections of hsdpa
            get_hsfach_connections      : get hsfach udp connection only
            merge_hsdpa_connections     : merge all hsdpa downlink udp connection data to a single csv file
            get_column                  : get specified column
Variables:
            dir                         : directory all csv file stored
            file_list                   : list of all csv files in the directory
            hsdpa_file_list             : list of all hsdpa udp connections
            header_dictionary           : dictionary of udp connection header
            header                      : list of header items
"""

class hspa_connection:

    def __init__(self, dir):
        self.dir = dir
        self.file_list = os.listdir(self.dir)
        self.hsdpa_file_list = []
        self.header_dictionary = {}
        self.header = []

        # We need to find all hspa udp connections
        for file in self.file_list:
            file_len = len(file)
            if (file.find("type2", 0, file_len) is not -1) or (file.find("type1", 0, file_len) is not -1) \
                    or (file.find("all_hsdpa", 0, file_len is not -1)):
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
                self.header = row
                line = ','.join(row)
                column = line.split(',')
                cell_index = 0
                for cell in column:
                    self.header_dictionary[cell] = cell_index
                    cell_index += 1

                return

    def get_file_list(self):
        return self.hsdpa_file_list


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

    def merge_hsdpa_connections(self):
        if len(self.hsdpa_file_list) is 0:
            print "No hsdpa connections found!!"
            return

        merged_file = "all_hsdpa.csv"
        with open(self.dir + '/' + merged_file, 'wb') as writer_file:
            csv_writer = csv.writer(writer_file)
            rows = []
            # write header
            # csv.writer(self.header)

            for file in self.hsdpa_file_list:
                with open(self.dir + '/' + file, 'rb') as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',', quotechar='|')
                    line_num = 0
                    for row in csv_reader:
                        if  line_num is not 0 and row[self.header_dictionary["congest"]] == "N/A":
                            rows.append(row)\
                            #csv_writer.writerow(row)
                        line_num += 1

            # sort frame no
            sortedlist = sorted(rows, key=lambda row: int(row[0]), reverse=False)
            csv_writer.writerow(self.header)
            csv_writer.writerows(sortedlist)

    def get_column(self, file_name, column_name):
        with open(self.dir + '/' + file_name, 'rb') as csv_file:
            csv_reader = csv.reader(csv_file)
            column = []
            row_num = 0
            for row in csv_reader:
                row_num += 1
                if row_num is 1:
                    continue
                column.append(row[self.header_dictionary[column_name]])
            return column

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Input parameter not enough!!\n\r"
        sys.exit(1)

    args = sys.argv
    hspa_conn_instance = hspa_connection(args[1])
    # hspa_conn_instance.get_hsfach_connections()
    #hspa_conn_instance.merge_hsdpa_connections()
    column = hspa_conn_instance.get_column("all_hsdpa.csv", "FrameNo")
    print column
