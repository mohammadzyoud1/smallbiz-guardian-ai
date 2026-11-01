from schema import Transaction

print(Transaction(date="2025-01-02", type="sale", category="sales", amount=420.5))
print(Transaction(date="2025-01-02", type="sale", category="suplies", amount=100))

try:
    Transaction(date="2025-01-02", type="sale", category="sales", amount=-5)
except Exception as error:
    print("Rejected:", error)