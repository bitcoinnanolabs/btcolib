from modules import btco
from configparser import ConfigParser


parser = ConfigParser()
config_files = parser.read('config.ini')


print("Config file successfully loaded")
btco_address = parser.get('wallet', 'address')
wallet_seed = parser.get('wallet', 'seed')
index = int(parser.get('wallet', 'index'))

amount = '1'

raw_amount = btco.convert(amount, 'BTCO', 'raw')


#First Receive
result = btco.process_pending(btco_address, index, wallet_seed)
print(result)

#Now send
dest_account = 'btco_1qa383yp4k7g318ikbripawehi7beqjodw9xot5sqpue8jut7u8dsuzpjz4y'
result = btco.send_btco(dest_account, raw_amount, btco_address, index, wallet_seed)
print(result)