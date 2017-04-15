"""
Interfaces:
            output_open                 : open output file
            output_close                : close output file
            write_analysis              : write one record to output
"""

file_handler = open("analysis_output.txt", "wb")


def output_open():
    return


def output_close():
    file_handler.close()


def write_analysis(record):
    file_handler.write(record + "\r\n")
