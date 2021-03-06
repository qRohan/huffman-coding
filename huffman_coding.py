#!/usr/bin/env python3

from __future__ import annotations
from collections import Counter
import os.path
import heapq
import pickle
import sys


__author__ = "Rohan Jakhar"

# Huffman Encoding and Decoding


class HuffmanCoding():
    def __init__(self):
        self.heap: list[HuffmanCoding.HeapNode] = []
        self.codes: dict[str, str] = {}
        self.reverse_mapping: dict[str, str] = {}

    class HeapNode():
        def __init__(self, freq: int):
            self.freq = freq

        def __lt__(self, other: HuffmanCoding.HeapNode):
            return self.freq < other.freq

        def __eq__(self, other: HuffmanCoding.HeapNode):
            return self.freq == other.freq

        def __gt__(self, other: HuffmanCoding.HeapNode):
            return self.freq > other.freq

    class HeapLeafNode(HeapNode):
        def __init__(self, char: str, freq: int):
            super().__init__(freq)
            self.char = char

        def __str__(self):
            return f"( {self.char}, {self.freq} )"

    class HeapInternalNode(HeapNode):
        def __init__(self, freq: int, left_node: HuffmanCoding.HeapNode, right_node: HuffmanCoding.HeapNode):
            super().__init__(freq)
            self.left = left_node
            self.right = right_node

        def __str__(self):
            return f"( freq: {self.freq}, left: {self.left}, right: {self.right} )"

    def make_tree(self):
        def make_heap(self: HuffmanCoding):
            count = Counter(self.text)
            for key in count.keys():
                heapq.heappush(self.heap, self.HeapLeafNode(key, count[key]))

        def merge_nodes(self: HuffmanCoding):
            while(len(self.heap) > 1):
                left = heapq.heappop(self.heap)
                right = heapq.heappop(self.heap)
                merged = self.HeapInternalNode(
                    right.freq + left.freq, left, right)
                heapq.heappush(self.heap, merged)

        make_heap(self)
        merge_nodes(self)
        self.huffman_tree = heapq.heappop(self.heap)

    def make_codes(self):
        def helper(node: HuffmanCoding.HeapNode, curr_code: str):
            if isinstance(node, HuffmanCoding.HeapInternalNode):
                helper(node.left, curr_code+'0')
                helper(node.right, curr_code+'1')
            elif isinstance(node, HuffmanCoding.HeapLeafNode):
                self.codes[node.char] = curr_code
                self.reverse_mapping[curr_code] = node.char

        helper(self.huffman_tree, "")

    def encode_text(self):
        def pad(self: HuffmanCoding):
            pad_needed = 8 - len(self.encoded_text) % 8
            pad_info = f"{pad_needed:08b}"
            self.encoded_padded_text = pad_info + self.encoded_text + "0"*pad_needed

        self.encoded_text = ''.join(self.codes[char] for char in self.text)
        pad(self)

        pad_text_lst = [int(self.encoded_padded_text[index:index+8], 2)
                        for index in range(0, len(self.encoded_padded_text), 8)]
        self.eptext_bytes = bytes(pad_text_lst)  # eptext= encoded padded text

    def decode_eptext(self):
        def unpad(self: HuffmanCoding):
            pad_info = int(self.encoded_padded_text[0:8], 2)
            self.encoded_text = self.encoded_padded_text[8: -1*pad_info]

        def decode_text(self: HuffmanCoding):
            curr_code = ""
            decoded_text_lst: list[str] = []
            for bit in self.encoded_text:
                curr_code += bit
                if curr_code in self.reverse_mapping:
                    char = self.reverse_mapping[curr_code]
                    decoded_text_lst.append(char)
                    curr_code = ""
            self.text = ''.join(decoded_text_lst)

        unpad(self)
        decode_text(self)

    def create_compressed_file(self):
        pickled = pickle.dumps(self.huffman_tree, protocol=-1)
        size = len(pickled)
        size_bin_str = f"{size:032b}"
        size_lst = [int(size_bin_str[index: index+8], 2)
                    for index in range(0, 32, 8)]
        size_bytes = bytes(size_lst)

        file_name: str = self.path+".bin"
        with open(file_name, "wb+") as handle:
            handle.write(size_bytes)
            handle.write(pickled)
            handle.write(self.eptext_bytes)
        self.compressed_size = os.path.getsize(file_name)

    def read_compressed_file(self, path: str):
        absolue_path = os.path.abspath(path)
        with open(absolue_path, "rb") as cfhandle:
            base_name = os.path.basename(absolue_path)
            self.path: str = os.path.splitext(base_name)[0]

            # can be using direct math
            tree_size_bin = ''.join(
                [f"{byte:08b}" for byte in cfhandle.read(4)])
            tree_size = int(tree_size_bin, 2)

            pickled_tree = cfhandle.read(tree_size)
            self.huffman_tree: HuffmanCoding.HeapNode = pickle.loads(
                pickled_tree)

            bit_string_list = [f"{byte:08b}" for byte in cfhandle.read()]
        self.encoded_padded_text = ''.join(bit_string_list)

    def read_uncompressed_file(self, path: str):
        absolue_path: str = os.path.abspath(path)
        self.uncompressed_size = os.path.getsize(absolue_path)
        with open(absolue_path, 'r') as fhandle:
            self.text = fhandle.read()
            base_name = os.path.basename(absolue_path)
            self.path, _ = os.path.splitext(base_name)

    def create_uncompressed_file(self):
        file_name: str = self.path+"_uncompressed.txt"
        with open(file_name, 'w') as fhandle:
            fhandle.write(self.text)

    def encode(self, path: str):
        self.read_uncompressed_file(path)
        self.make_tree()
        self.make_codes()
        self.encode_text()
        self.create_compressed_file()

    def decode(self, path: str):
        self.read_compressed_file(path)
        self.make_codes()
        self.decode_eptext()
        self.create_uncompressed_file()


if __name__ == "__main__":
    x = HuffmanCoding()
    file_name = sys.argv[-1]
    method = sys.argv[-2]
    method = method.lower()
    if method == 'e' or method == 'encode':
        x.encode(file_name)
        print(f"Compression ratio: {x.uncompressed_size / x.compressed_size}")

    elif method == 'd' or method == 'decode':
        x.decode(file_name)
    else:
        print("Invalid method")
        sys.exit(0)
