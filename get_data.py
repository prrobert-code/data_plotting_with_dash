import numpy as np
import pandas as pd
import os


class GetData:
    def __init__(self):
        self.folder_dir = ''
        self.file_list = []
        self.file_list_short = []
        self.file_type = '.plt'
        self.data_container = {'x': [], 'y': [], 'file': [], 'curve_identifier': []}
        self.current_item_container = []
        self.curve_save_counter = 1

    def save_file_to_file_list(self, filelist):
        for file in filelist:
            if file not in self.file_list:
                self.file_list.append(file)
                self.file_list_short.append(file.split('/')[-1])
        return self.file_list, self.file_list_short

    def get_file_list_from_folder(self, folder_dir):
        file_list = []
        try:
            for item in os.listdir(folder_dir):
                if os.path.isfile(os.path.join(folder_dir, item)):
                    if self.file_type in item:
                        file_list.append(item)
        except FileNotFoundError:
            return []
        return file_list


    def parse_file(self, filename):
        if filename.split('.')[-1] == 'csv':
            data = pd.read_csv(filename)
            for col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
            if 'arc_length' in data.columns:
                data['arc_length'] = data['arc_length'] * 1.0e4
            data['file'] = filename
            return data

        if filename.split('.')[-1] == 'plt':
            # f = open(filename)
            with open(filename) as f:
                datasets = []
                functions = []
                data = []
                # Extract datasets
                for line in f:
                    if "datasets" in line:
                        break

                for line in f:
                    datasets.append(line.rstrip().split("\""))
                    if "]" in line:
                        break
                # Flatten datasets list
                datasets = [item for sublist in datasets for item in sublist]
                # Remove empty strings
                datasets = list(filter(None, [item.strip() for item in datasets]))[:-1]
                length = len(datasets)

                # Extract data
                for line in f:
                    if "Data" in line:
                        break
                for line in f:
                    data.append(line.rstrip().split(" "))
                    if "}" in line:
                        break
                # Flatten data list
                data = [item for sublist in data for item in sublist]
                # Remove empty strings
                data = ' '.join(data).split()[:-1]
                # Split data in rows
                data = [data[x:x + length] for x in range(0, len(data), length)]

                df = pd.DataFrame(data, columns=datasets, dtype='float64')
                df['file'] = filename
                return df




if __name__ == '__main__':
    data_reader = GetData()



