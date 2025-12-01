import psycopg2

conn = psycopg2.connect(dbname='irf_dev', user='irf_user', password='irf_pass', host='localhost', port=5433)
cur = conn.cursor()

# Check items
cur.execute('SELECT uid, component_type, lot_number, qr_image_url, created_at FROM items ORDER BY created_at DESC LIMIT 5')
rows = cur.fetchall()
print('Recent items in database:')
print('=' * 80)
for row in rows:
    print(f'UID: {row[0]}')
    print(f'Type: {row[1]}, Lot: {row[2]}')
    print(f'QR URL: {row[3]}')
    print(f'Created: {row[4]}')
    print('-' * 80)

# Check engraving queue
cur.execute('SELECT id, item_uid, status, svg_url FROM engraving_queue ORDER BY created_at DESC LIMIT 5')
queue_rows = cur.fetchall()
print('\nEngraving Queue:')
print('=' * 80)
for row in queue_rows:
    print(f'Job ID: {row[0]}, Item UID: {row[1]}, Status: {row[2]}, URL: {row[3]}')

cur.close()
conn.close()
