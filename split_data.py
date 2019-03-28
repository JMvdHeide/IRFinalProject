#!/usr/bin/python3
# The file cutter 3000
# This script will take an argument that needs to be a file
# it will randomise this file so everything is in another place
# After that it will cut 80% and write it to a train file and the same with 10% for a test file and development file


import sys, random


def read_file(file):
    """Read in the file, split each line and get only the text."""
    print('##### Reading data...')
    with open(file, "r") as f:
        data = list()
        for line in f.readlines():
            line = line.split('\t')
            data.append(line[1])
    f.close()
    return data

def write_to_file(training, test, development):
    """Write training, test and development data to all correct files."""
    print('##### Writing to files training, test and development...')
    with open('train.txt', 'w')as f:
        for line in training:
            f.write(line)
    f.close()
    with open('test.txt', 'w')as f:
        for line in test:
            f.write(line)
    f.close()
    with open('dev.txt', 'w')as f:
        for line in development:
            f.write(line)
    f.close()

def split_and_write_files(data):
    """Shuffle the data and split them into training, test and development set."""
    print('##### Spliting data...')
    random.shuffle(data)
    len_data = len(data)
    len_training_data = int(len_data * 0.8)
    len_test_data = int(len_data * 0.1)
    training_data = data[:len_training_data]
    test_data = data[len_training_data:len_training_data + len_test_data]
    development_data = data[len_training_data + len_test_data: len_training_data + len_test_data + len_test_data]
    write_to_file(training_data, test_data, development_data)


def main():
    if len(sys.argv) > 1 and len(sys.argv) < 3:
        print('##### Welcome to the The file cutter 3000')
        data = read_file(sys.argv[1])
        split_and_write_files(data)
        print('##### Done! Created training_data.txt, test_data.txt and development_data.txt')
    else:
        print('You have to add an argument that represents a file to be splited.')

if __name__ == '__main__':
    main()
