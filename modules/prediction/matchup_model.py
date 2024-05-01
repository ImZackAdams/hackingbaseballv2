# File: modules/prediction/matchup_model.py

from sqlalchemy import create_engine
import pandas as pd
from modules.prediction.preprocessor import preprocess_data
from modules.prediction.model import train_model

def predict_game_outcome():
    engine = create_engine('sqlite:///baseball_data.db')
    query = "SELECT * FROM statcast_data"
    df = pd.read_sql(query, engine)

    # Preprocess the data
    preprocessed_df = preprocess_data(df)

    # Train the model
    model = train_model(preprocessed_df)

    # Make predictions or perform other operations with the trained model
    # ...

    return model