""""Business" logic for pointsbot."""

import re
from datetime import datetime

class CommandException(Exception):
    """Something went wrong processing the command."""

class PointsProcessor:
    """Processor of points transactions."""

    def __init__(self, *, points_db, currency_symbol):
        self.points_db = points_db
        # Note: all are 4 letters - this allows faster processing
        self.command_map = {
            "!gran": self.grant,
            "!hist": self.history,
            "!give": self.give,
            "!send": self.give,
            "!take": self.take,
            "!help": self.help,
            "!undo": self.undo,
            "!lead": self.lead,
            "!wall": self.wallet
            }
        self.currency_symbol = currency_symbol

    def is_command(self, message):
        """Returns true if the message is a known command."""
        if not message.content.startswith("!"):
            return False

        return message.content[:5] in self.command_map

    def process(self, message):
        """Parse and run the given command."""
        return self.command_map[message.content[:5]](message)

    def grant(self, message):
        """Grant points to a user from the bank."""
        parsed = re.search(r"!grant? <@(\d+)> \$?(\d+) ?(.*)", message.content)
        if not parsed:
            raise CommandException(f"Failed to parse !grant command. `{message.content}`")
        self.points_db.grant_points(
            user_from=message.author.id,
            user_to=parsed[1],
            amount=float(parsed[2]),
            command="!grant",
            note=parsed[3],
            deduct_from=False)
        return f"<@{message.author.id}> granted {self.currency_symbol}{parsed[2]} to <@{parsed[1]}>!"

    def give(self, message):
        """Give points to one user from another."""
        parsed = re.search(r"!give <@(\d+)> \$?(\d+) ?(.*)", message.content)
        if not parsed:
            raise CommandException(f"Failed to parse !give command. `{message.content}`")
        if message.author.id == int(parsed[1]):
            raise CommandException(
                "Giving points to yourself doesn't do anything.\n"
                "(Use !grant to get them from the bank.)")
        self.points_db.grant_points(
            user_from=message.author.id,
            user_to=parsed[1],
            amount=float(parsed[2]),
            command="!give",
            note=parsed[3],
            deduct_from=True)
        return f"Gave {self.currency_symbol}{parsed[2]} from <@{message.author.id}> to <@{parsed[1]}>!"

    def history(self, message):
        """Retrive historic actions."""
        parsed = re.search(r"!histo?r?y? ?(\d*) ?(\d*)", message.content)
        if not parsed:
            raise CommandException(f"Failed to parse !hist[ory] command. `{message.content}`")
        length = 10 if not parsed[1] else int(parsed[1])
        if length > 20:
            raise CommandException("Cannot get more than 20 rows using !hist[ory]")
        offset = 0 if not parsed[2] else int(parsed[2])
        history = self.points_db.get_history(length, offset)
        def ellipse(string):
            return string[:20] + "..." if len(string) > 20 else string
        return "\n".join(
            (f"{datetime.utcfromtimestamp(h[5]).strftime('%Y-%m-%d %H:%M:%S')} "
              f"<@{h[0]}> -> "
              f"<@{h[1]}> "
              f"{self.currency_symbol}{h[2]} "
              f"({h[3]})" +
              ((' \"' + (ellipse(h[4]) + '\"') if h[4] else '')))
            for h in history)

    def take(self, message):
        """Takes points from the user and gives them to the bank"""
        parsed = re.search(r"!take <@(\d+)> \$?(\d+) ?(.*)", message.content)
        if not parsed:
            raise CommandException(f"Failed to parse !take command. `{message.content}`")
        self.points_db.take_points(
            user_from=message.author.id,
            user_to=parsed[1],
            amount=float(parsed[2]),
            command="!take",
            note=parsed[3])
        return (f"<@{message.author.id}> Took {self.currency_symbol}{parsed[2]} "
               f"away from <@{parsed[1]}> and gave it to the bank!")

    def help(self, _):
        """Display a help message"""
        return f"""
Pointsbot (by Erty)

Letters in [square brackets] are optional - e.g. !hist and !history are the same.

!gran[t] @User 100 - Give @User {self.currency_symbol}100 from the bank.

!give @User 100 - Give @User {self.currency_symbol}100 of your money.
!send @User 100 - Alias of !give.

!take @User 100 - Take {self.currency_symbol}100 of @User's money and give it to the bank.

!help - Display this text.

!undo - Undo the last transaction by you.

!lead[erboard] - Show the current leaderboard.

!wall[et] - Show your current money amount.
!wall[et] @User - Show the current balance for @User.

!hist[ory] - Show the last 20 transactions.
!hist[ory] 10 - Show the last 10 transactions.
!hist[ory] 10 20 - Show 10 transactions starting 20 transactions ago.
        """

    def undo(self, _):
        """Undo the last action done by the current user."""
        return "Sorry, not implemented yet!"

    def lead(self, _):
        """Show the current leaderboard."""
        leaderboard = self.points_db.get_leaderboard(10, 0)
        return "\n".join(f"<@{l[0]}>: {self.currency_symbol}{l[1]}" for l in leaderboard)

    def wallet(self, message):
        """Show balance for current user."""
        parsed = re.match(r"!walle?t? ?<?@?(\d*)>?", message.content)
        if not parsed:
            raise CommandException(f"Failed to parse !wall[et] command. `{message.content}`")

        user = int(parsed[1]) if parsed[1] else message.author.id
        result = self.points_db.get_balance(user)
        if result is None:
            return f"<@{user}> has {self.currency_symbol}0"
        return f"<@{user}> has {self.currency_symbol}{result[1]}"
