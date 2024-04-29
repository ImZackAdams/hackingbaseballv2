from database import db
import datetime


class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    home_team = db.Column(db.String(100))
    away_team = db.Column(db.String(100))

    # Add any other fields you want to store for each game

    def __repr__(self):
        return f'<Game {self.home_team} vs {self.away_team} on {self.date}>'
