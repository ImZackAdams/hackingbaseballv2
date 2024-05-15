from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    # Dummy data for testing
    games = [
        {
            'away_team': 'Team A',
            'home_team': 'Team B',
            'prediction': 'Team B Wins',
            'odds': '-110'
        },
        {
            'away_team': 'Team C',
            'home_team': 'Team D',
            'prediction': 'Team C Wins',
            'odds': '+120'
        }
    ]
    # Render the results template with the dummy data
    return render_template('results.html', games=games)

if __name__ == '__main__':
    app.run(debug=True)