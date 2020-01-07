import pickle

from PIL import Image
from bitarray import bitarray

from huffman_coding.HuffmanTree import HuffmanTree


# In case of image, we give image_path to the constructor
huffman_tree = HuffmanTree(file_path='deadpool.bmp', is_image=True)
huffman_tree.create_tree()

# root_node = huffman_tree.root_node
compressed_file_data = huffman_tree.get_compressed_file(key=2)

print(compressed_file_data[0])

meta_data = compressed_file_data[0]
bit_array = compressed_file_data[1]

# print(meta_data)

with open('metadata.dat', 'wb') as fp:
    pickle.dump(meta_data, fp)

# bit_array = bitarray(binary_presentation)

with open('compressed.bin', 'wb') as fp:
    fp.write(bit_array)

print(huffman_tree.root_node.frequency) ## TODO: DEBUG line
