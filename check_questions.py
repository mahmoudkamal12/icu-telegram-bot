import sqlite3
import json

def check():
    db = sqlite3.connect('bot_data.db')
    cursor = db.cursor()
    cursor.execute('SELECT question, options, correct_index, explanation FROM current_polls ORDER BY rowid DESC LIMIT 3')
    rows = cursor.fetchall()
    
    with open('questions_review.txt', 'w', encoding='utf-8') as f:
        for i, row in enumerate(rows):
            f.write(f"--- Question {i+1} ---\n")
            f.write(f"Q: {row[0]}\n")
            f.write(f"Options: {row[1]}\n")
            f.write(f"Correct Index: {row[2]}\n")
            f.write(f"Explanation: {row[3]}\n\n")
    db.close()

if __name__ == '__main__':
    check()
