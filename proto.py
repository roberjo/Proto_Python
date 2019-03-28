import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict

# dependencies can be any iterable with strings, 
# e.g. file line-by-line iterator
dependencies = [
  'pandas>=0.24.1',
  'numpy>=1.16.2',
  'tabulate>=0.8.3'
]

# Here, if a pip package dependency is not met, 
# a DistributionNotFound or VersionConflict
# exception is thrown. 
try:
    pkg_resources.require(dependencies)
except Exception as e: 
    print("**ERROR** Package not found!")
    print(e)
    print("Please install the missing package with \'pip install [x]\'")
    print(" where [x] is the package name.")
    raise SystemExit

import numpy as np
import struct
import pandas as pd
from datetime import datetime
from tabulate import tabulate

HEADER_LENGTH = 9
BASE_RECORD_LENGTH = 13
DOLLAR_AMOUNT_LENGTH = 8
DEBIT = 'Debit'
CREDIT = 'Credit'
START = 'StartAutopay'
END = 'EndAutopay'

# All multi-byte fields are encoded in network byte order (Big-endian) 
# => struct.unpack format code = '>'.
# Header:
# | 4 byte magic string "MPS7" | 1 byte version | 4 byte (uint32) # of records |
# The header contains the canonical information about how the records should be processed.
# Note: there are fewer than 100 records in `txnlog.dat`.
# Record:
# | 1 byte record type enum | 4 byte (uint32) Unix timestamp | 8 byte (uint64) user ID |

HEADER_FORMAT = '>4sBI' # 4-byte string, 1-byte unsigned char, 4-byte uint32
RECORD_FORMAT = '>cIQ' # 1-byte char, 4-byte uint32, 8-byte uint64
DOLLAR_FORMAT = '>d' # 8-byte double

# Dictionary of transaction log record types
RECORD_TYPES = {
    b'\x00': DEBIT,
    b'\x01': CREDIT,
    b'\x02': START,
    b'\x03': END
}

def parse_file(name):
    with open(name,mode='rb') as lines:
        transaction_log = lines.read()

    # Parse header line
    (log_format, version, num_records) = struct.unpack(
        HEADER_FORMAT, 
        transaction_log[0:HEADER_LENGTH]
        )
    print('Log Format:', log_format.decode())
    print('Version: ', version)
    print('Record Count: ', num_records)
    
    transactions = pd.DataFrame(
        columns=['Record Type', 'Timestamp', 'User ID', 'Dollar Amount']
        )
    record_start = HEADER_LENGTH

    # Parse records and populate dataframe
    for i in range(num_records):
        dollar_amount = None
        record_stop = record_start + BASE_RECORD_LENGTH
        (record_type_enum, timestamp, user_id) = struct.unpack(
            RECORD_FORMAT, 
            transaction_log[record_start:record_stop]
            )
        record_start = record_stop

        record_type = RECORD_TYPES[record_type_enum]        
        if record_type in [DEBIT, CREDIT]:
            record_stop = record_start + DOLLAR_AMOUNT_LENGTH
            dollar_amount = struct.unpack(
                DOLLAR_FORMAT, 
                transaction_log[record_start:record_stop]
                )[0] #[0] - unpack always returns tuple, even if only one entry
            record_start = record_stop

        # Add sign to DEBITs
        if record_type == DEBIT:
            dollar_amount = dollar_amount * -1

        # Convert unix timestamp to datetime
        UnixDate = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

        # Collect records in dataframe
        transactions.loc[i] = [record_type, UnixDate, user_id, dollar_amount]

    return transactions


# Function that returns the total dollar amount of a given transaction_type
# (DEBIT or CREDIT) for a given user_id if supplied, or for all users if not,
# rounded to two decimal places.
def total_transaction_amount(transactions, transaction_type, user_id=None):
    if user_id:
        is_user = transactions['User ID'] == user_id
        transactions = transactions[is_user]
        
    is_transaction_type = transactions['Record Type'] == transaction_type
    return round(transactions[is_transaction_type]['Dollar Amount'].sum(), 2)


# Function that returns the total number of Autopay changes of a given type
# (START or END).
def num_autopay_changes(transactions, change_type):
    is_change_type = transactions['Record Type'] == change_type
    return transactions[is_change_type]['Record Type'].count()

# Function that returns the balance of a user for all records in the file
def user_balance(transactions, userid):
    total_user_debits = total_transaction_amount(transactions, DEBIT, userid)
    total_user_credits = total_transaction_amount(transactions, CREDIT, userid)
    return total_user_credits + total_user_debits
    
# Main Entry Point of the Application
def main():

    print("""\
      ___           ___           ___           ___           ___     
     /\\  \\         /\\  \\         /\\  \\         /\\  \\         /\\  \\    
    /::\\  \\       /::\\  \\       /::\\  \\        \\:\\  \\       /::\\  \\   
   /:/\\:\\  \\     /:/\\:\\  \\     /:/\\:\\  \\        \\:\\  \\     /:/\\:\\  \\  
  /::\\~\\:\\  \\   /::\\~\\:\\  \\   /:/  \\:\\  \\       /::\\  \\   /:/  \\:\\  \\ 
 /:/\\:\\ \\:\\__\\ /:/\\:\\ \\:\\__\\ /:/__/ \\:\\__\\     /:/\\:\\__\\ /:/__/ \\:\\__\\ 
 \\/__\\:\\/:/  / \\/_|::\\/:/  / \\:\\  \\ /:/  /    /:/  \\/__/ \\:\\  \\ /:/  /
      \\::/  /     |:|::/  /   \\:\\  /:/  /    /:/  /       \\:\\  /:/  / 
       \\/__/      |:|\\/__/     \\:\\/:/  /     \\/__/         \\:\\/:/  /  
                  |:|  |        \\::/  /                     \\::/  /   
                   \\|__|         \\/__/                       \\/__/    """)
    transactions = parse_file('txnlog.dat')

    print("\r\nQuestion Answers")

    # Answer the required questions
    total_debits = total_transaction_amount(transactions, DEBIT)
    print('\r\nWhat is the total amount in dollars of debits? \r\nTotal Debits: {}'.format(total_debits))

    total_credits = total_transaction_amount(transactions, CREDIT)
    print('\r\nWhat is the total amount in dollars of credits? \r\nTotal Credits: {}'.format(total_credits))

    num_autopays_started = num_autopay_changes(transactions, START)
    print('\r\nHow many autopays were started? \r\nAutopays Started: {}'.format(num_autopays_started))

    num_autopays_ended = num_autopay_changes(transactions, END)
    print('\r\nHow many autopays were ended? \r\nAutopays Ended: {}'.format(num_autopays_ended))

    target_user_id = 2456938384156277127
    usr_balance = user_balance(transactions, target_user_id)
    print('\r\nWhat is balance of user ID 2456938384156277127? \r\nBalance of user {user_id}: {user_balance}'.format(
        user_id=target_user_id, user_balance=usr_balance
    ))

    # Data Integrity Sanity Checks
    # Uncomment the lines below to check the integrity of the 
    # input data file.

    # #Get max dollar amount
    # max_dollar = transactions['Dollar Amount'].max()
    # print('Max Dollar: ', round(max_dollar, 2))
    
    # # Get the min dollar amount
    # min_dollar = transactions['Dollar Amount'].min()
    # print('Min Dollar: ', round(min_dollar, 2))
    
    # # Group the transactions by each user, and get the individual max and min
    # trans_groupby = transactions.groupby('User ID').agg({'Dollar Amount':['max','min']}).fillna(0)
    # print(tabulate(trans_groupby, headers='keys', tablefmt='psql'))
    
    # # Print the raw transaction records sorted by userid, and timestamp asc
    # sorted_transactions = transactions.sort_values(['User ID', 'Timestamp']).fillna(0)
    # print(tabulate(sorted_transactions, headers='keys', tablefmt='psql'))


if __name__ == '__main__':
    main()