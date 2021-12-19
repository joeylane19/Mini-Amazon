import csv
import numpy
from PIL import Image
products = []

with open("data/Products.csv") as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        imarray = numpy.random.rand(100,100,3) * 255
        im = Image.fromarray(imarray.astype('uint8')).convert('RGBA')
        word = row[2].split(' ')
        f = ""
        for w in word:
            f+= w
        f+=".png"
        im.save(f)
        row[5] = f
        products.append(row)
    print(products)

with open("data/Products.csv", 'w') as output:
    csvwriter = csv.writer(output)
    for row in products:
        csvwriter.writerow(row)