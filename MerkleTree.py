import hashlib
import math


class Node:
    def __init__(self, value):
        self.left = None
        self.right = None
        self.value = value
        self.hash = calculate_hash(self.value)


def calculate_hash(value):
    return hashlib \
        .sha256(value.encode('utf-8')) \
        .hexdigest()


def build_merkle_tree(leaves):
    # construct the bottom layer
    current_layer_nodes = []
    for i in leaves:
        current_layer_nodes.append(Node(i))

    while len(current_layer_nodes) != 1:

        # construct the next layer based on the current layer
        next_layer_nodes = []
        for i in range(0, len(current_layer_nodes), 2):  # [0, 2, 4, 6,...]

            # pick two adjecent child nodes
            node1 = current_layer_nodes[i]
            node2 = current_layer_nodes[i + 1]
            # print(f'left hash: {node1.hash}')
            # print(f'right hash: {node2.hash}')

            # construct a parent node
            concat_hash = node1.hash + node2.hash
            parent = Node(concat_hash)
            parent.left = node1
            parent.right = node2
            # print(f'parent hash: {parent.hash}\n')
            next_layer_nodes.append(parent)

        current_layer_nodes = next_layer_nodes

    return current_layer_nodes[0].hash


def padding(leaves):
    size = len(leaves)
    if size == 0:
        return ['']
    reduced_size = int(math.pow(2, int(math.log2(size))))
    pad_size = 0
    if reduced_size != size:
        pad_size = 2 * reduced_size - size
    for i in range(pad_size):
        leaves.append('')
    return leaves


def genMerkleRoot(leaves):
    leaves = padding(leaves)
    # print("Leaves:", leaves)

    merkle_root = build_merkle_tree(leaves)
    return merkle_root


if __name__ == '__main__':
    leaves = ['We', 'are', 'PolyU', 'Together', 'We', 'Excel']
    merkle_root = genMerkleRoot(leaves)
    print(f'\nmerkle root: {merkle_root}\n')
