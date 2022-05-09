import  json
import binascii
from bitstring import BitArray
from pyblake2 import blake2b
from btco25519.btco25519 import ed25519_oop as ed25519

from decimal import Decimal
from hashlib import blake2b
import  requests


from configparser import ConfigParser
import os
thisfolder = os.path.dirname(os.path.abspath(__file__))
initfile = os.path.join(thisfolder, '../config.ini')

parser = ConfigParser()
config_files = parser.read(initfile)

representative = parser.get('backend', 'representative')
url_address = parser.get('backend', 'url_address')

time_out = 3

def private_public(private):
    return ed25519.SigningKey(private).get_verifying_key().to_bytes()


def btco_account(address):
    # Given a string containing an BTCO address, confirm validity and
    # provide resulting hex address
    if len(address) == 65 and (address[:5] == 'btco_'):
        # each index = binary value, account_lookup[0] == '1'
        account_map = "13456789abcdefghijkmnopqrstuwxyz"
        account_lookup = {}
        # populate lookup index with prebuilt bitarrays ready to append
        for i in range(32):
            account_lookup[account_map[i]] = BitArray(uint=i ,length=5)

        # we want everything after 'btco_' but before the 8-char checksum
        acrop_key = address[5:-8]
        # extract checksum
        acrop_check = address[-8:]

        # convert base-32 (5-bit) values to byte string by appending each
        # 5-bit value to the bitstring, essentially bitshifting << 5 and
        # then adding the 5-bit value.
        number_l = BitArray()
        for x in range(0, len(acrop_key)):
            number_l.append(account_lookup[acrop_key[x]])
        # reduce from 260 to 256 bit (upper 4 bits are never used as account
        # is a uint256)
        number_l = number_l[4:]

        check_l = BitArray()
        for x in range(0, len(acrop_check)):
            check_l.append(account_lookup[acrop_check[x]])

        # reverse byte order to match hashing format
        check_l.byteswap()
        result = number_l.hex.upper()

        # verify checksum
        h = blake2b(digest_size=5)
        h.update(number_l.bytes)
        if (h.hexdigest() == check_l.hex):
            return result
        else:
            return False
    else:
        return False


def account_btco(account):
    # Given a string containing a hex address, encode to public address
    # format with checksum
    # each index = binary value, account_lookup['00001'] == '3'
    account_map = "13456789abcdefghijkmnopqrstuwxyz"
    account_lookup = {}
    # populate lookup index for binary string to base-32 string character
    for i in range(32):
        account_lookup[BitArray(uint=i ,length=5).bin] = account_map[i]
    # hex string > binary
    account = BitArray(hex=account)

    # get checksum
    h = blake2b(digest_size=5)
    h.update(account.bytes)
    checksum = BitArray(hex=h.hexdigest())

    # encode checksum
    # swap bytes for compatibility with original implementation
    checksum.byteswap()
    encode_check = ''
    for x in range(0 ,int(len(checksum.bin ) /5)):
        # each 5-bit sequence = a base-32 character from account_map
        encode_check += account_lookup[checksum.bin[ x *5: x * 5 +5]]

    # encode account
    encode_account = ''
    while len(account.bin) < 260:
        # pad our binary value so it is 260 bits long before conversion
        # (first value can only be 00000 '1' or 00001 '3')
        account = '0b0' + account
    for x in range(0 ,int(len(account.bin ) /5)):
        # each 5-bit sequence = a base-32 character from account_map
        encode_account += account_lookup[account.bin[ x *5: x * 5 +5]]

    # build final address string
    return 'btco_' +encode_account +encode_check


def seed_account(seed, index):
    # Given an account seed and index #, provide the account private and
    # public keys
    h = blake2b(digest_size=32)

    seed_data = BitArray(hex=seed)
    seed_index = BitArray(int=index ,length=32)

    h.update(seed_data.bytes)
    h.update(seed_index.bytes)

    account_key = BitArray(h.digest())
    return account_key.bytes, private_public(account_key.bytes)


def receive_btco(index, account, wallet_seed):
    # Get pending blocks

    rx_data = get_pending(str(account))
    if len(rx_data) == 0:
        return

    for block in rx_data:
        #print(block)
        block_hash = block
        #print(rx_data[block])
        balance = int(rx_data[block]['amount'])
        source = rx_data[block]['source']

    previous = get_previous(str(account))

    current_balance = get_balance(previous)
    if current_balance == 'timeout':
        return 'timeout'
    #print(current_balance)
    new_balance = int(current_balance) + int(balance)
    hex_balance = hex(new_balance)
    #print(hex_balance)
    hex_final_balance = hex_balance[2:].upper().rjust(32, '0')
    #print(hex_final_balance)

    priv_key, pub_key = seed_account(wallet_seed, int(index))
    public_key = ed25519.SigningKey(priv_key).get_verifying_key().to_ascii(encoding="hex")

    # print("Starting PoW Generation")
    work = get_pow(previous)
    if work == 'timeout':
        return 'timeout'
    # print("Completed PoW Generation")

    # Calculate signature
    bh = blake2b(digest_size=32)
    bh.update(BitArray(hex='0x0000000000000000000000000000000000000000000000000000000000000006').bytes)
    bh.update(BitArray(hex=btco_account(account)).bytes)
    bh.update(BitArray(hex=previous).bytes)
    bh.update(BitArray(hex=btco_account(account)).bytes)
    bh.update(BitArray(hex=hex_final_balance).bytes)
    bh.update(BitArray(hex=block_hash).bytes)

    sig = ed25519.SigningKey(priv_key +pub_key).sign(bh.digest())
    signature = str(binascii.hexlify(sig), 'ascii')

    finished_block = '{ "type" : "state", "previous" : "%s", "representative" : "%s" , "account" : "%s", "balance" : "%s", "link" : "%s", \
            "work" : "%s", "signature" : "%s" }' % \
    (previous, account, account, new_balance, block_hash, work, signature)

    data = requests.post(url_address, json = {"action" : "process", "subtype" : "receive", "block" : finished_block}, timeout=time_out)
    block_reply = data.json()
    return block_reply, balance

def get_address(index, wallet_seed):
    # Generate address
    print("Generate Address")
    priv_key, pub_key = seed_account(wallet_seed, int(index))
    public_key = str(binascii.hexlify(pub_key), 'ascii')
    print("Public Key: ", str(public_key))

    account = account_btco(str(public_key))
    print("Account Address: ", account)
    return account

def open_btco(index, account, wallet_seed):
    # Get pending blocks

    rx_data = get_pending(str(account))
    for block in rx_data:
        #print(block)
        block_hash = block
        #print(rx_data[block])
        balance = int(rx_data[block]['amount'])
        source = rx_data[block]['source']

    hex_balance = hex(balance)
    #print(hex_balance)
    hex_final_balance = hex_balance[2:].upper().rjust(32, '0')
    #print(hex_final_balance)

    priv_key, pub_key = seed_account(wallet_seed, int(index))
    public_key = ed25519.SigningKey(priv_key).get_verifying_key().to_ascii(encoding="hex")

    # print("Starting PoW Generation")
    work = get_pow(str(public_key, 'ascii'))
    # print("Completed PoW Generation")

    # Calculate signature
    bh = blake2b(digest_size=32)
    bh.update(BitArray(hex='0x0000000000000000000000000000000000000000000000000000000000000006').bytes)
    bh.update(BitArray(hex=btco_account(account)).bytes)
    bh.update(BitArray(hex='0x0000000000000000000000000000000000000000000000000000000000000000').bytes)
    bh.update(BitArray(hex=btco_account(account)).bytes)
    bh.update(BitArray(hex=hex_final_balance).bytes)
    bh.update(BitArray(hex=block_hash).bytes)

    sig = ed25519.SigningKey(priv_key + pub_key).sign(bh.digest())
    signature = str(binascii.hexlify(sig), 'ascii')

    finished_block = '{ "type" : "state", "previous" : "0000000000000000000000000000000000000000000000000000000000000000", "representative" : "%s" , "account" : "%s", "balance" : "%s", "link" : "%s", \
            "work" : "%s", "signature" : "%s" }' % (account, account, balance, block_hash, work, signature)
    
    data = requests.post(url_address, json = {"action" : "process", "subtype" : "open", "block" : finished_block}, timeout=time_out)
    block_reply = data.json()
    return block_reply, balance


def send_btco(dest_account, amount, account, index, wallet_seed):

    previous = get_previous(str(account))

    current_balance = get_balance(previous)
    #print(current_balance)
    new_balance = int(current_balance) - int(amount)
    hex_balance = hex(new_balance)

    #print(hex_balance)
    hex_final_balance = hex_balance[2:].upper().rjust(32, '0')
    #print(hex_final_balance)

    priv_key, pub_key = seed_account(wallet_seed, int(index))
    public_key = ed25519.SigningKey(priv_key).get_verifying_key().to_ascii(encoding="hex")

    # print("Starting PoW Generation")
    work = get_pow(previous)
    # print("Completed PoW Generation")

    # Calculate signature
    bh = blake2b(digest_size=32)
    bh.update(BitArray(hex='0x0000000000000000000000000000000000000000000000000000000000000006').bytes)
    bh.update(BitArray(hex=btco_account(account)).bytes)
    bh.update(BitArray(hex=previous).bytes)
    bh.update(BitArray(hex=btco_account(account)).bytes)
    bh.update(BitArray(hex=hex_final_balance).bytes)
    bh.update(BitArray(hex=btco_account(dest_account)).bytes)

    sig = ed25519.SigningKey(priv_key + pub_key).sign(bh.digest())
    signature = str(binascii.hexlify(sig), 'ascii')

    finished_block = '{ "type" : "state", "previous" : "%s", "representative" : "%s" , "account" : "%s", "balance" : "%s", "link" : "%s", \
            "work" : "%s", "signature" : "%s" }' % (
    previous, account, account, new_balance, dest_account, work, signature)

    data = requests.post(url_address, json = {"action" : "process", "subtype" : "send", "block" : finished_block}, timeout=time_out)
    block_reply = data.json()
    return block_reply


def get_pow(hash):
    data = requests.post(url_address, json = {"action" : "work_generate", "hash" : hash, "multiplier" : "1.0"}, timeout=30)
    #Generate work
    resulting_data = data.json()
    if 'work' in resulting_data:
        work = resulting_data['work']
        print(work)
    else:
        work = 'error'
    return work


def get_previous(account):
    # Get account info
    accounts_list = [account]
    try:
        data = requests.post(url_address, json = {"action":"accounts_frontiers", "accounts" : accounts_list}, timeout=time_out)
    except requests.exceptions.Timeout:
        print("Error: Timeout")
        return "timeout"

    account_info = data.json()

    if len(account_info['frontiers']) == 0:
        return ""
    else:
        previous = account_info['frontiers'][account]
        return previous


def get_balance(hash):
    # Get balance from hash
    try:
        data = requests.post(url_address, json = {"action":"block", "hash" : hash}, timeout=time_out)
    except requests.exceptions.Timeout:
        print("Error: Timeout")
        return "timeout"

    rx_data = data.json()
    if "error" in rx_data:
        return ""
    else:
        new_rx = json.loads(str(rx_data['contents']))
        return new_rx['balance']

def get_account_balance(account):
    # Get balance from hash
    try:
        data = requests.post(url_address, json = {"action":"account_balance", "account" : account}, timeout=time_out)
    except requests.exceptions.Timeout:
        print("Error: Timeout")
        return "timeout"

    rx_data = data.json()
    #print(rx_data)
    if "error" in rx_data:
        return ""
    else:
        #new_rx = json.loads(str(rx_data['contents']))
        return rx_data['balance']

def get_pending(account):
    try:
        data = requests.post(url_address, json = {"action":"pending", "count" : "1", "account" : account, "source" : "true"}, timeout=time_out)
    except requests.exceptions.Timeout:
        print("Error: Timeout")
        return "timeout"

    rx_data = data.json()

    return rx_data['blocks']

def process_pending(account, index_pos, wallet_seed):
    pending = get_pending(str(account))
    previous = get_previous(str(account))
    if len(pending) > 0:
        if len(previous) == 0:
            print("Opening Account")
            hash, balance = open_btco(int(index_pos), account, wallet_seed)
            previous = get_previous(str(account))
            return hash
        else:
            hash, balance = receive_btco(int(index_pos), account, wallet_seed)
            return hash
    else:
        return 0



"""
Conversion tools for converting Nano units
Units source: https://github.com/btcocurrency/btco-node/wiki/Distribution,-Mining-and-Units
Gbtco/Gxrb/Grai = 1000000000000000000000000000000000raw, 10^33
Mbtco/Mxrb/Mrai = 1000000000000000000000000000000raw, 10^30
kbtco/kxrb/krai = 1000000000000000000000000000raw, 10^27
btco/xrb/rai  = 1000000000000000000000000raw, 10^24
mbtco/mxrb/mrai = 1000000000000000000000raw, 10^21
ubtco/uxrb/urai = 1000000000000000000raw, 10^18
1 raw is the smallest possible division
Mbtco used to be called Mxrb or Mrai
1 btco (formerly xrb or rai) is 10^24 raw
Mbtco is also called BTCO, or in the past XRB
"""

BASE_UNIT = 'raw'
UNIT_NAMES = ['xrb', 'rai', 'btco']
UNITS_TO_RAW = {BASE_UNIT: Decimal(1)}


def _populate_units():
    # populate the existing units, eg krai, Mrai, Mxrb, Gbtco etc.
    for name in UNIT_NAMES:
        for i, prefix in enumerate(['G', 'M', 'k', '', 'm', 'u']):
            in_raw = 10 ** (33 - (i * 3))
            unit_name = prefix + name
            UNITS_TO_RAW[unit_name] = Decimal(in_raw)

    # special case for XRB
    UNITS_TO_RAW['XRB'] = UNITS_TO_RAW['Mbtco']
    UNITS_TO_RAW['BTCO'] = UNITS_TO_RAW['Mbtco']


def convert(value, from_unit, to_unit):
    """
    Converts a value from `from_unit` units to `to_unit` units
    :param value: value to convert
    :type value: int or str or decimal.Decimal
    :param from_unit: unit to convert from
    :type from_unit: str
    :param to_unit: unit to convert to
    :type to_unit: str
    >>> convert(value='1.5', from_unit='xrb', to_unit='krai')
    Decimal('0.0015')
    """

    if isinstance(value, float):
        raise ValueError(
            "float values can lead to unexpected precision loss, please use a"
            " Decimal or string eg."
            " convert('%s', %r, %r)" % (value, from_unit, to_unit)
        )

    if from_unit not in UNITS_TO_RAW:
        raise ValueError('unknown unit: %r' % from_unit)

    if to_unit not in UNITS_TO_RAW:
        raise ValueError('unknown unit: %r' % to_unit)

    try:
        value = Decimal(value)
    except Exception:
        raise ValueError('not a number: %r' % value)

    from_value_in_base = UNITS_TO_RAW[from_unit]
    to_value_in_base = UNITS_TO_RAW[to_unit]

    result = value * (from_value_in_base / to_value_in_base)

    return result.normalize()


_populate_units()