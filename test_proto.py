import unittest
import pandas as pd 
import proto  

# initialize list of data 
data = [
    ['Debit', '2014-07-10 13:52:37',  61122968712918070, -272.89], 
    ['Debit', '2014-07-10 13:52:37',  61122968712918070, -272.89], 
    ['Credit', '2014-07-10 13:52:37',  61122968712918070, 272.89], 
    ['Credit', '2014-07-10 13:52:37',  61122968712918070, 272.89], 
    ['StartAutopay', '2014-07-10 13:52:37', 61122968712918070], 
    ['EndAutopay', '2014-07-10 13:52:37', 61122968712918070], 
    ]

# Create the pandas DataFrame 
df = pd.DataFrame(data, columns=['Record Type', 'Timestamp', 'User ID', 'Dollar Amount']) 

# Import the needed functions for test purposes
total_transaction_amount = proto.total_transaction_amount
num_autopay_changes = proto.num_autopay_changes
user_balance = proto.user_balance

class TestProto(unittest.TestCase):
    def test_total_transaction_sum_debits(self):
        """
        Test that it can sum all records
        total_transaction_amount(transactions, transaction_type, user_id=None)
        """
        result = total_transaction_amount(df, 'Debit')
        self.assertEqual(result, -545.78)

    def test_total_transaction_sum_credits(self):
        """
        Test that it can sum all records
        total_transaction_amount(transactions, transaction_type, user_id=None)
        """
        result = total_transaction_amount(df, 'Credit')
        self.assertEqual(result, 545.78)

    def test_user_balance(self):
        """
        Test that it can sum all records for a user
        user_balance(transactions, userid)
        """
        result = user_balance(df, 61122968712918070)
        self.assertEqual(result, 0)

    def test_num_autopay_changes_start(self):
        """
        num_autopay_changes(transactions, change_type)
        """
        result = num_autopay_changes(df, 'StartAutopay')
        self.assertEqual(result, 1)

    def test_num_autopay_changes_end(self):
        """
        num_autopay_changes(transactions, change_type)
        """
        result = num_autopay_changes(df, 'EndAutopay')
        self.assertEqual(result, 1)

if __name__ == '__main__':
    unittest.main()