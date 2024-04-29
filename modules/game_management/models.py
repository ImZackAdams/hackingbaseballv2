
#from app import db
import datetime

class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100))
    stadium = db.Column(db.String(100))

    # Define a relationship to games
    home_games = db.relationship('Game', back_populates='home_team')
    away_games = db.relationship('Game', back_populates='away_team')

    def __repr__(self):
        return f'<Team {self.name}>'

class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    team_home_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    team_away_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)

    # Define the relationship to teams
    home_team = db.relationship('Team', foreign_keys=[team_home_id], back_populates='home_games')
    away_team = db.relationship('Team', foreign_keys=[team_away_id], back_populates='away_games')

    def __repr__(self):
        return f'<Game {self.home_team.name} vs {self.away_team.name} on {self.date}>'
