import sqlite3

conn = sqlite3.connect('pharmacy_local.db')
cursor = conn.cursor()

# Check batches
cursor.execute("SELECT COUNT(*) FROM batches")
batch_count = cursor.fetchone()[0]
print(f"=== BATCHES: {batch_count} total ===")

cursor.execute("""
    SELECT b.id, b.batch_number, b.medicine_id, m.name, b.quantity, b.expiration_date, b.is_active
    FROM batches b 
    JOIN medicines m ON b.medicine_id = m.id
    ORDER BY b.medicine_id, b.expiration_date
    LIMIT 15
""")
for row in cursor.fetchall():
    print(f"  #{row[0]} | {row[1]} | Med: {row[3][:25]} | Qty: {row[4]} | Exp: {row[5]} | Active: {row[6]}")

# Check medicines with stock
cursor.execute("SELECT COUNT(*) FROM medicines WHERE quantity > 0 AND is_active = 1")
med_with_stock = cursor.fetchone()[0]
print(f"\n=== MEDICINES with stock: {med_with_stock} ===")

conn.close()
