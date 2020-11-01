import os
from utils import *
from PIL import Image

class EU4_Flag_Converter:
    def __init__(self):
        pass

    def process_flags(self, images, results):
        create_folder(results)
        for filename in os.listdir(images):
            in_file = os.path.join(images, filename)
            out_file = os.path.join(results, os.path.splitext(filename)[0] + ".png")
            image = Image.open(in_file)
            image.save(out_file)
        return results

if __name__ == "__main__":
    c = EU4_Flag_Converter()
    c.process_flags("../../raw_data/eu4/flags", "results/images")
