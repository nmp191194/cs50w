import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    headers = next(reader, None)  # returns the headers or `None` if the input is empty
    if headers:
        print("Skipped header row: " + str(headers))
    nrow = 0
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
        nrow += 1
    db.commit()
    print(f"Successfully imported {nrow} books!")

if __name__ == "__main__":
    main()
