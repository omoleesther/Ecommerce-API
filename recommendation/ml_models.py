import pandas as pd  # to load the dataset
import numpy as np
import joblib
from database import engine
from scipy.sparse import hstack, csr_matrix
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

# To load the entire table from the SQL database as a Pandas dataframe, we will:Establish the connection with our database by providing the database URL.Use the `pd.read_sql_table` function to load the entire table and convert it into a Pandas dataframe. The function requires table name, engine objects, and column names. Display the the entire rows.

# joining product and category to get the category name


class RecommendationModel:
    def __init__(self):

        query = """
        SELECT p.id, p.name, p.description, p.price, c.name as category_name
        From products p
        Join categories c on p.category_id = c.id

        """
        # This fetches your product data from the database including the category name from the join. You now have a DataFrame with name, description, price and category_name columns.
        df = pd.read_sql(query, con=engine)
        self.df = df
        print(df)

    def train(self):

        # the column you want to one-Hot encode
        categorical_columns = ['category_name']

        # creates a One-Hot Encoder object. sparse_output=False means return a regular array instead of a compressed format which is easier to work with.

        encoder = OneHotEncoder(sparse_output=False)

        # it converts the column to number
        one_hot_encoded = encoder.fit_transform(self.df[categorical_columns])

        # creates a new dataframe for the encoded dolumn
        one_hot_df = pd.DataFrame(
            one_hot_encoded, columns=encoder.get_feature_names_out(categorical_columns))

        # combines the original dataframe and the encoded one
        df_encoded = pd.concat([self.df, one_hot_df], axis=1)

        # drops the original category column
        df_encoded = df_encoded.drop(categorical_columns, axis=1)
        # print(df_encoded)
        # print(df_encoded.columns.tolist())

        # converting description and name to tfidf
        self.df['text'] = self.df['name'] + ' ' + \
            self.df['description'].fillna("")

        # Get TF-IDF value
        # it removes words that are common stop_words
        tfidf = TfidfVectorizer(stop_words="english")
        result = tfidf.fit_transform(self.df['text'])

        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(self.df[['price']])
        # print(scaled_data)

        # matrix converts datframe(df) to matrix
        num_scaled_data = csr_matrix(scaled_data)
        one_hot_sparse = csr_matrix(one_hot_encoded)
        tfidf_sparse = result

        # hstack is used to combine all 3 into 1 matrix
        combined_data = hstack([one_hot_sparse, tfidf_sparse, num_scaled_data])
        print("Data:", combined_data)
        # Fit the KNN Model:We fit the KNN model using the normalized user-item matrix. The metric='cosine' parameter specifies that we use cosine similarity to measure the similarity between users.basically we're training and saving the model
        self.knn = NearestNeighbors(metric='cosine', algorithm='brute')
        self.knn.fit(combined_data)
        self.combined_data = combined_data

    def save(self):
        # Serialization is the process of converting an object’s state into a format that can be stored or transmitted and later reconstructed.
        joblib.dump(self.knn, "trained_models/recommendation.pkl")

    def load(self):
        # load the model from file
        self.knn_from_joblib = joblib.load(
            'trained_models/recommendation.pkl')

    def recommend(self, product_id):
        product_row = self.df.loc[self.df['id'] == product_id]
        product_index = product_row.index[0]
        product_vector = self.combined_data[product_index]
        # distances — how far each similar product is
        # indices — the row positions of the similar products
        distances, indices = self.knn.kneighbors(product_vector)
        similar_products = self.df.iloc[indices[0]].to_dict('records')
        return similar_products


model = RecommendationModel()
model.train()
model.save()
model.load()
print(model.recommend(1))

"""
# Display IDF values
print('\nidf values:')
for ele1, ele2 in zip(tfidf.get_feature_names_out(), tfidf.idf_):
    print(ele1, ':', ele2)

# Display TF-IDF values along with indexing
print('\nWord indexes:')
print(tfidf.vocabulary_)
print('\ntf-idf value:')
print(result)
print('\ntf-idf values in matrix form:')
print(result.toarray())
"""

"""
df = pd.read_sql_table(
    "products".join("categories"),
    con=engine,
    columns=['name', 'description', 'price', 'category_id', 'name']
)
df.head()
"""
