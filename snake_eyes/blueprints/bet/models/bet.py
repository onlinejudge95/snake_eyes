from lib.src.util_datetime import tz_aware_datetime
from lib.src.util_sqlalchemy import ResourceMixin
from snake_eyes.extensions import db


class Bet(ResourceMixin, db.Model):
    __tablename__ = "bets"
    id = db.Column(db.Integer, primary_key=True)

    # Relationships
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        index=True, nullable=False
    )

    # Attributes for betting
    guess = db.Column(db.Integer())
    dice_1 = db.Column(db.Integer())
    dice_2 = db.Column(db.Integer())
    roll = db.Column(db.Integer())
    wagered = db.Column(db.BigInteger())
    payout = db.Column(db.Float())
    net = db.Column(db.BigInteger())

    def __init__(self, **kwargs):
        super(Bet, self).__init__(**kwargs)

    @classmethod
    def is_winner(cls, guess, roll):
        """
        Determine if the result is a win or loss for the player

        :param guess: Dice guess
        :type guess: int
        :param roll: Dice roll
        :type roll: int
        :return: bool
        """
        return guess == roll

    @classmethod
    def determine_payout(cls, payout, is_winner):
        """
        Determine the payout.

        :param payout: Dice guess
        :type payout: float
        :param is_winner: Was the bet won or lost
        :type is_winner: bool
        :return: int
        """
        return payout if is_winner else 1.0

    @classmethod
    def calculate_net(cls, wagered, payout, is_winner):
        """
        Calculate the net won or lost.

        :param wagered: Dice guess
        :type wagered: int
        :param payout: Dice roll
        :type payout: float
        :param is_winner: Was the bet won or lost
        :type is_winner: bool
        :return: int
        """
        return int(wagered * payout) if is_winner else -wagered

    def save_and_update_user(self, user):
        """
        Commit the bet and update the user's information.

        :return: SQLAlchemy save result
        """
        self.save()

        user.coins += self.net
        user.last_bet_on = tz_aware_datetime()

        return user.save()

    def to_json(self):
        """
        Return JSON fields to represent a bet.

        :return: dict
        """
        return {
            "guess": self.guess,
            "die_1": self.dice_1,
            "die_2": self.dice_2,
            "roll": self.roll,
            "wagered": self.wagered,
            "payout": self.payout,
            "net": self.net,
            "is_winner": Bet.is_winner(self.guess, self.roll)
        }
