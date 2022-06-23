import requests, random
from optparse import OptionParser

host = "www.kickinganimal.nl"
port = 8080

parser = OptionParser()
parser.add_option('-c', '--connect', action="store_true", help='simulate new connection to the server')
parser.add_option('-s', '--status', type="choice", choices=[ "gevangen", "actief", "offline", "0", "1", "2" ], help='set status of the trap')
parser.add_option('-m', '--mac', type='string', help='mac-address to use, otherwise random.')
parser.add_option('-i', '--val_id', type='string', help='val ID to use, otherwise random.')

opt, args = parser.parse_args()

if (opt.connect is None) == (opt.status is None):
    print("Error: either '--connect' or '--status' has to be specified")
    print()
    parser.print_help()
    exit()

if opt.mac:
    mac = opt.mac
else:
    mac = ''.join([ random.choice('0123456789ABCDEF') for _ in range(12) ])

if opt.val_id:
    valId = opt.val_id
else:
    valId = ''.join([ random.choice('0123456789') for _ in range(12) ])

print('using val ID:', valId, "and using mac-address:", mac)

if opt.connect:
    res = requests.post(f'https://{host}:{port}/app/connect', json={ 'valMac': mac, 'val_ID': valId }, verify=False)
    print('\n\n\n->', res.json()['error'])

elif opt.status == 'offline' or opt.status == "0":
    res = requests.post(f'https://{host}:{port}/app/valUpdate', json={ 'valMac': mac, 'val_ID': valId, 'valStatus': 0 }, verify=False)
    print('\n\n\n->', res.json()['error'])
elif opt.status == 'actief' or opt.status == "1":
    res = requests.post(f'https://{host}:{port}/app/valUpdate', json={ 'valMac': mac, 'val_ID': valId, 'valStatus': 1 }, verify=False)
    print('\n\n\n->', res.json()['error'])
elif opt.status == 'gevangen' or opt.status == "2":
    res = requests.post(f'https://{host}:{port}/app/valUpdate', json={ 'valMac': mac, 'val_ID': valId, 'valStatus': 2 }, verify=False)
    print('\n\n\n->', res.json()['error'])