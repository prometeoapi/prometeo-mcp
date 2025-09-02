

1. List Accounts

"""
Get all accounts for the current merchant, format result in a snippet txt table (tabular)
"""


2. Get Account Transactions


"""
Get all transactions for a merchant account by account_id, format result in a snippet txt table (tabular)

(short ID (only first 8 digits) same to reference and mask destination account)
"""


3. List Customers

"""
Get all customers for the current merchant, format result in a snippet txt table (tabular)
"""

4. Get Customer details

"""
Get a customer details by customer_id, format result in a snippet txt table (tabular)
"""


4.1. Create Customer

"""
Create a customer:
- tax_id_type: rfc
- tax_id: BTA160616Q24
- name: BANCO DE TAPITAS AC
- external_id: "PROM001.BTA"
- withdrawal_accounts: 
    account_number: 012680001108499959
    bicfi: BCMRMXMM
    selected: true
"""


5. Transfer

"""
I want to transfer 0.01 MXN to that customer, origin: ea530790-bddb-4bfe-95b7-410ca1ec6e7e
"""

5.1. Check transfer status

"""
Get a transfer status by transfer_id, format result in a snippet txt table (tabular)
"""


6. Charges

"""
I have to charge my customers (from the list of customers, save the customer_id uuid), with 10 MXN the services of the company. Create a charge intent for the customers with at least 1 withdrawal account. Use  destination: ea530790-bddb-4bfe-95b7-410ca1ec6e7e.

Return a list of customers.external_id and the virtual account assigned for each customer.
"""
