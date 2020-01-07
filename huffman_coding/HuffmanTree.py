import collections

from bitarray import bitarray
from PIL import Image

from .node import Node


class HuffmanTree:
    elements_dict = {}
    encoded_elements = {}
    nodes_list = []
    base_nodes = []
    elements_length = 0
    garbage_bits = 0
    decoded_data = ''
    root_node = None
    image_size = None
    image_path = None
    is_image = False
    is_decompression = False
    encoded_data = bitarray()

    def __init__(self,
                 data=None,
                 elements_dict=None,
                 file_path=None,
                 is_image=False,
                 is_decompression=False):
        """
        DO NOT ENTER ALL ARGUMENTS, ONLY FEW OF THEM IS NEEDED FOR IT TO WORK
        elements_dict is the dictionary of values and their frequencies.
        FOR COMPRESSION:
        In case of image, provide 'image_path'.
        In case of text, provide data (string).
        FOR DECOMPRESSION:
        provide 'elements_dict' for decompression. TODO: re-document it
        :type data: str (in case of text)
        :type elements_dict: dict
        :type file_path: str
        """
        self.data = data
        self.is_image = is_image
        self.is_decompression = is_decompression
        if is_image:
            if self.is_decompression:
                self.garbage_bits = elements_dict.pop('g_bits')
                self.image_size = elements_dict.pop('image_size')
                self.elements_dict = elements_dict
            else:
                img = Image.open(file_path)
                # self.image_mode = img.mode
                self.image_size = img.size
                print('SIZEEEEEEEEEEEEE')
                print(self.image_size)
                data = img.getdata()
                print('DATAAAAAAAAAAAAAAA')
                print(data)
                data_list = []
                for tup in list(data):
                    for val in tup:
                        data_list.append(val)
                self.data = data_list
                self.create_elements_dict()
        else:
            # in case of text compression, we provide data to constructor
            if self.is_decompression:
                # for decompression
                self.elements_dict = elements_dict
                self.garbage_bits = elements_dict.pop('g_bits')
            else:
                # for compression
                # if user entered text then create elements_dict
                self.create_elements_dict()

    def create_elements_dict(self):
        """Creates elements_dict based on the text"""
        for data in self.data:
            if data in self.elements_dict:
                self.elements_dict[data] += 1
                continue
            self.elements_dict[data] = 1

        self.elements_length = len(self.elements_dict)

    def sort_elements_dict(self):
        """This method sorts the elements_dict in ascending order based on the
        frequencies"""
        # Creating a sorted list of tuples of value and frequency
        sorted_list = sorted(self.elements_dict.items(), key=lambda kv: kv[1])
        # Converting the list of tuples into dictionary
        self.elements_dict = collections.OrderedDict(sorted_list)

    def create_base_nodes(self):
        """Creates base (leaf) nodes of the tree"""
        self.sort_elements_dict()
        for key in self.elements_dict:
            node = Node(value=key,
                        frequency=self.elements_dict[key],
                        is_leaf=True)
            self.nodes_list.append(node)

        self.base_nodes = self.nodes_list.copy()

    def insert_single_node(self, node):
        """Inserts a single node into the nodesList in the sorted manner"""
        # if len(self.nodesList) == 0:
        #     self.nodesList.append(node)

        for i in range(len(self.nodes_list)):
            if self.nodes_list[i].frequency > node.frequency:
                self.nodes_list.insert(i, node)
                return

        self.nodes_list.append(node)

    def create_tree(self):
        self.create_base_nodes()
        #  TODO: Delete the line below after debugging
        print(f'{len(self.nodes_list)} total nodes')
        i = 0
        """Creates huffman tree based on 'elements_dict'"""
        while len(self.nodes_list) > 1:
            left_node = self.nodes_list[i]
            right_node = self.nodes_list[i+1]
            left_node.is_left_child = True
            right_node.is_right_child = True
            combined_frequency = left_node.frequency + right_node.frequency
            current_node = Node(left=left_node,
                                right=right_node,
                                frequency=combined_frequency)
            current_node.left.parent = current_node
            current_node.right.parent = current_node
            # Deleting the first two nodes that are in the current_node
            del self.nodes_list[0:2]
            self.insert_single_node(current_node)

        self.root_node = self.nodes_list[0]

    def encode_elements(self):
        """Maps the binary encoding of the corresponding element into a dic"""
        # binary_encoding = []
        # binary_encoding = ''

        for i in range(len(self.base_nodes)):
            binary_encoding = ''
            current_node = self.base_nodes[i]
            while current_node.parent is not None:
                if current_node.is_left_child:
                    # binary_encoding.insert(0, '0')
                    binary_encoding = '0' + binary_encoding
                if current_node.is_right_child:
                    # binary_encoding.insert(0, '1')
                    binary_encoding = '1' + binary_encoding
                current_node = current_node.parent

                self.encoded_elements[self.base_nodes[i].value] = binary_encoding

    def compress(self, key):
        """Compresses the data in binary string"""
        self.encode_elements()

        for element in self.data:
            # self.encoded_data += self.encoded_elements[element]
            for bit in self.encoded_elements[element]:
                if bit == '0':
                    self.encoded_data.append(False)
                    print(self.encoded_data)
                    continue
                if bit == '1':
                    self.encoded_data.append(True)
                    print(self.encoded_data)

        print('ENC DATA::::::::')
        print(self.encoded_data)
        print('')
        print(len(self.encoded_data))
        print('BEFORE BIN CONVERSION:::::::::')
        print(key)
        print('AFTER::::::::::::')
        binary_key = bin(key)[2:]
        print(len(binary_key))
        print(binary_key)
        starting_bits = '0' * (8 - len(binary_key))
        print(starting_bits)
        binary_key = starting_bits + binary_key
        print(binary_key)
        self.encoded_data = bitarray(binary_key) + self.encoded_data

        self.garbage_bits = 8 - (len(self.encoded_data) % 8)
        self.elements_dict['g_bits'] = self.garbage_bits
        print('GARBAGE:::')
        print(self.elements_dict['g_bits'])

    @staticmethod
    def read_and_get_from_file(file_path):
        """Reads data from file and returns the dict with encoded_data $ key"""
        bit_array = bitarray()
        with open(file_path, 'rb') as fp:
            # noinspection PyArgumentList
            bit_array.fromfile(fp)
        key = bit_array[:8]
        binary_presentation = bit_array[8:]
        binary_presentation_length = len(binary_presentation)
        binary_presentation.tobytes()
        print('to bytes::::')
        print(binary_presentation)
        byte_presentation_int = int.from_bytes(binary_presentation,
                                               byteorder='big',
                                               signed=False)
        print('int byte::')
        print(byte_presentation_int)
        encoded_data = bin(byte_presentation_int)[2:]
        print('again::')
        print(encoded_data)
        significant_bits_length = binary_presentation_length - len(
            encoded_data)
        significant_bits = '0' * significant_bits_length
        encoded_data = significant_bits + encoded_data
        return {'key': key, 'encoded_data': encoded_data}

    def decompress(self, encoded_file_data):
        """Decompresses the file based on elements_dict"""
        pixel = []
        pixels_list = []
        self.create_tree()
        # current_node = self.root_node

        for i in range(self.garbage_bits):
            encoded_file_data = encoded_file_data[:-1]

            # while sum(map(len, self.decoded_data)) != self.root_node.frequency:
        while len(encoded_file_data) >= 1:
            # TODO: DEBUG LINE BELOW
            # print(sum(map(len, pixels_list)))
            current_node = self.root_node
            while not current_node.is_leaf:
                if encoded_file_data[0] == '0':
                    current_node = current_node.left
                    encoded_file_data = encoded_file_data[1:]
                    continue
                if encoded_file_data[0] == '1':
                    current_node = current_node.right
                    encoded_file_data = encoded_file_data[1:]
                    continue
            if self.is_image:
                pixel.append(current_node.value)
                if len(pixel) == 3:
                    pixels_list.append(tuple(pixel))
                    pixel = []
                    self.decoded_data = pixels_list
            else:
                self.decoded_data = self.decoded_data + current_node.value
                print('leaf :')
                print(self.decoded_data)
        print(self.decoded_data)

    def get_compressed_file(self, key):
        """Returns the compressed file which contains compressed_text and
         encoded_elements"""
        self.compress(key)
        if self.is_image:
            self.elements_dict['image_size'] = self.image_size
        return [self.elements_dict, self.encoded_data]

    def __repr__(self):
        return f'root_node(frequency: {self.root_node.frequency})'

