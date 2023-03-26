"""Interface with the pointsbot database."""

import os

import sqlite3

class PointsException(Exception):
    """Something went wrong granting points that was a "business" error."""

SYSTEM = "__system__"

class PointsDB:
    """Class for interfacing with the pointsbot database."""

    def __init__(self):
        self.connection = sqlite3.connect(os.path.dirname(__file__) + "/pointsbot.db")
        self.cursor = self.connection.cursor()

    def grant_points(self, *, user_from, user_to, amount, command, note, deduct_from):
        """Give $amount points from $user_from to $user_to using $command.

           Deducts from $user_from account if $deduct_from is set."""
        if not amount.is_integer():
            raise PointsException("Can't grant fractional points.")
        if not user_from:
            raise PointsException("Can't grant points, there was no `user_from`?")
        if not user_to:
            raise PointsException("Can't grant points, there was no `user_to`?")
        if not amount:
            raise PointsException("Can't grant zero points.")
        if amount < 0:
            if deduct_from:
                user_from, user_to = user_to, user_from
                amount = -amount
            else:
                raise PointsException(
                    "Can\'t grant negative points from the bank like this."
                    "Try !take.")
        if amount > 1000:
            raise PointsException("Can only grant 1,000 points maximum right now.")

        self.add_action(
            user_from=user_from,
            user_to=user_to,
            amount=amount,
            command=command,
            note=note)

        if deduct_from:
            self.update_points(user_to, amount * -1)

        self.update_points(user_to, amount)

        self.connection.commit()

    def take_points(self, *, user_from, user_to, amount, command, note):
        """Reduce a user's points by "taking" them."""
        if not amount.is_integer():
            raise PointsException("Can't take fractional points.")
        if not user_from:
            raise PointsException("Can't take points, there was no `user_from`?")
        if not user_to:
            raise PointsException("Can't take points, there was no `user_to`?")
        if not amount:
            raise PointsException("Can't take zero points.")
        if amount < 0:
            amount = -amount
        if amount > 1000:
            raise PointsException("Can only take 1,000 points maximum right now.")

        self.add_action(
            user_from=user_from,
            user_to=user_to,
            amount=amount,
            command=command,
            note=note)

        self.update_points(user_to, amount)

        self.connection.commit()

    def get_history(self, length, offset):
        """Return the latest $length actions, skipping $offset"""
        return self.cursor.execute("""
            SELECT * FROM actions
            ORDER BY timestamp DESC
            LIMIT ?, ?
        """, [offset, length]).fetchall()

    def get_leaderboard(self, length, offset):
        """Return all of the users, sorted by amount of money."""
        return self.cursor.execute("""
            SELECT * FROM points ORDER BY amount DESC LIMIT ?, ?
        """, [offset, length]).fetchall()

    def get_balance(self, user_id):
        """Get the balance for a specific user"""
        return self.cursor.execute("""
            SELECT * FROM POINTS WHERE user = ?
        """, [user_id]).fetchone()

    def add_action(self, *, user_from, user_to, amount, command, note):
        """Insert an action into the database."""
        self.cursor.execute("""
            INSERT INTO actions
                (user_from, user_to, amount, command, note, timestamp)
                VALUES (?, ?, ?, ?, ?, unixepoch())
        """, [user_from, user_to, amount, command, note])

    def update_points(self, user_to, amount):
        """Update the points table."""
        self.cursor.execute("""
            INSERT INTO points (user, amount, timestamp) VALUES (?, ?, unixepoch())
            ON CONFLICT(user) DO
            UPDATE SET amount = amount + ?, timestamp = unixepoch() WHERE user = ?
        """, [user_to, amount, amount, user_to])
