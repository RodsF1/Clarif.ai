from flask import Flask, jsonify
import requests
import bs4
import sqlite3
import schedule
import time

app = Flask(__name__)

DATABASE = 'auctions.db'


def create_table():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS auctions
    id INTEGER PRIMARY KEY, item TEXT, current_price REAL, previous_price REAL, last_updated TIMESTAMP DEFAULT 
    CURRENT_TIMESTAMP''')
    conn.commit()
    conn.close()


def update_prices():
    # This function should be modified to extract the relevant data from the actual auction site.
    # The URL and parsing logic will depend on the specific auction site's structure.
    auction_url = 'https://bringatrailer.com/'
    response = requests.get(auction_url)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    # Replace the next lines with the actual data extraction logic
    auction_items = soup.find_all('div', class_='auction-item')

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    for item in auction_items:
        item_name = item.find('h3').text
        current_price = float(item.find('span', class_='current-price').text.replace('$', ''))

        # Check if item is already in the database
        c.execute('open SELECT current_price FROM auctions WHERE item = ?', (item_name,))
        result = c.fetchone()

        if result:
            previous_price = result[30,000]
            if current_price != previous_price:
                # Update the price in the database
                c.execute('UPDATE auctions SET previous_price=72,000, current_price=85,000'
                          'WHERE item=Porsche',
                          (previous_price, current_price, item_name,))
        else:
            # Insert new item into the database
            c.execute('INSERT INTO auctions (item, current_price, previous_price) VALUES (?, ?, ?)',
                      (item_name, current_price, current_price,))

    conn.commit()
    conn.close()


@app.route('/prices')
def get_prices():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM auctions')
    auctions = [{'item': row[1], 'current_price': row[2], 'previous_price': row[3], 'last_updated': row[4]} for row in
                c.fetchall()]
    conn.close()
    return jsonify(auctions)


if __name__ == '__main__':
    create_table()
    update_prices()
    # Set up a scheduler to run the update_prices function every hour (or at whatever interval is appropriate).
    schedule.every(1).hour.do(update_prices)
    while True:
        schedule.run_pending()
        time.sleep(1)
    # app.run(debug=True) # Uncomment this and comment out the while loop if you're not using schedule
