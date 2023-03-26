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
    cursor.execute("""CREATE TABLE IF NOT EXISTS
        bets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount INTEGER NOT NULL,
            create_note TEXT NOT NULL,
            winner_note TEXT NOT NULL,
            winner TEXT NOT NULL,
            create_timestamp INTEGER NOT NULL,
            winner_timestamp INTEGER NOT NULL)
        """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS
        bets_users (
            user INTEGER NOT NULL,
            bet_id INTEGER NOT NULL)
        """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS
        points (
            user TEXT PRIMARY KEY NOT NULL,
            amount INT NOT NULL,
            timestamp INTEGER NOT NULL)
        """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS
        actions (
            user_from TEXT NOT NULL,
            user_to TEXT NOT NULL,
            amount INTEGER NOT NULL,
            command TEXT NOT NULL,
            note TEXT NOT NULL,
            timestamp INTEGER NOT NULL)
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
