# https://learnblockchain.cn/2017/10/27/build_blockchain_by_python/

import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis Block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        # Creates a new Block and adds it to the chain
        """
        生成新块
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Blockchain
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of current_transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self):
        # Adds a new transaction to the list of transactions
        """
        生成新交易信息，信息将加入到下一个待挖的区块中
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    def proof_of_work(self, last_proof):
        """
        简单的工作量证明：
        - 查找一个p’ 使得hash(pp') 以4个0开头
        - p 是上一个块的证明，p’ 是当前的证明
        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @property
    def last_block(self):
        # Returns the last Block in the chain
        return self.chain[-1]

    @staticmethod
    def hash(block):
        # Hashes a Block
        """
        生成块的 SHA-256 hash值
        :param block: <dict> Block
        :return: <str>
        """

        # We must make sure that the Dictionary is ordered, or we'll have
        # inconssitent Hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        验证证明：是否hash(last_proof, proof) 以4个0开头？
        :param last_proof: <int> Previous proof
        : param proof: <int> Current proof_of_work
        :return: <bool> True if correct, False if not.
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == '0000'


# Instantiate our Node 创建一个节点
app = Flask(__name__)

# Generate a globally unique address for this Node 为节点创建一个随机的名字
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain 实例Blockchain类
blockchain = Blockchain()


# 创建/mine GET接口
@app.route('/mine', methods=['GET'])
def mine():
    return 'We will mine a new Block'


# 创建/transactions/new POST接口,可以给接口发送交易数据
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'],
                                       values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


# 创建 /chain 接口, 返回整个区块链
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


# 服务运行在端口5000上
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=500)
