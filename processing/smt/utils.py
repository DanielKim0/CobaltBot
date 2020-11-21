import os

def split_list(data, length):
    return [data[i * length:(i + 1) * length] for i in range((len(data) + length - 1) // length)]

def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
