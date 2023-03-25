"""Wrapper around sqlite for creating/destroying the pointsbot db file."""

import argparse
import sqlite3

def parse_args():
    """Set up argparse."""
    parser = argparse.ArgumentParser(description="Create tables for pointsbot.")
    parser.add_argument("-d", "--drop",
                    action="store_true", help="Drop tables before recreating")
    return parser.parse_args()

def drop_tables(cursor):
    """Drop existing tables."""
    print("Dropping tables")
    cursor.execute("DROP TABLE IF EXISTS points")
    cursor.execute("DROP TABLE IF EXISTS actions")


def create_tables(cursor):
    """Create needed tables."""
    print("Creating tables")
    cursor.execute("""CREATE TABLE
        points (
            user TEXT PRIMARY KEY NOT NULL,
            amount INT NOT NULL,
            timestamp INTEGER NOT NULL
        ) STRICT
    """)
    cursor.execute("""CREATE TABLE
        actions (
            user_from TEXT NOT NULL,
            user_to TEXT NOT NULL,
            amount INTEGER NOT NULL,
            command TEXT NOT NULL,
            note TEXT NOT NULL,
            timestamp INTEGER NOT NULL
        ) STRICT
    """)

def run(args):
    """Run requested db commands"""
    connection = sqlite3.connect("pointsbot.db")
    cursor = connection.cursor()

    if args.drop:
        print("Confirm drop tables y/N?")
        confirm = input()
        if confirm == "y":
            drop_tables(cursor)
    create_tables(cursor)


if __name__ == "__main__":
    run(parse_args())
