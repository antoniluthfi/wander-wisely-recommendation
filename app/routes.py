import random
import pandas as pd
from flask import request, jsonify
from app import app, mysql
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from decimal import Decimal


@app.route('/', methods=['GET'])
@app.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 10, type=int)
    offset = (page - 1) * per_page

    cur = mysql.connection.cursor()
    cur.execute(
        """SELECT 
            tourism_attractions.*, 
            tourism_types.name AS tourism_type_name, 
            tourism_files.tourism_attraction_id, 
            GROUP_CONCAT(tourism_files.filename) AS filename, 
            GROUP_CONCAT(tourism_files.path) AS path
        FROM tourism_attractions 
        LEFT JOIN tourism_types ON tourism_attractions.tourism_type_id = tourism_types.id 
        LEFT JOIN tourism_files ON tourism_attractions.id = tourism_files.tourism_attraction_id
        GROUP BY tourism_attractions.id
        LIMIT %s OFFSET %s
        """, (per_page, offset))
    tourism_attractions = cur.fetchall()

    cur.execute("SELECT COUNT(*) AS count FROM tourism_attractions")
    total_items = cur.fetchall()[0]['count']

    attractions_df = pd.DataFrame(tourism_attractions)
    attractions_df['filename'] = attractions_df['filename'].str.split(
        ',').tolist()
    attractions_df['path'] = attractions_df['path'].str.split(
        ',').tolist()

    return jsonify({
        "success": True,
        "data": attractions_df.to_dict(orient='records'),
        'total': total_items
    })


def sort(x):
    return x


@app.route('/recommendation', methods=['POST'])
def get_recommendation():
    print(request.args.get('hobbies'))
    if request.headers['Content-Type'] == 'application/json':
        try:
            body = request.get_json()
            cur = mysql.connection.cursor()

            # Get tourism_attractions data
            cur.execute(
                """SELECT 
                        tourism_attractions.*, 
                        tourism_types.name AS tourism_type_name, 
                        tourism_files.tourism_attraction_id, 
                        GROUP_CONCAT(tourism_files.filename) AS filename, 
                        GROUP_CONCAT(tourism_files.path) AS path
                    FROM tourism_attractions 
                    LEFT JOIN tourism_types ON tourism_attractions.tourism_type_id = tourism_types.id 
                    LEFT JOIN tourism_files ON tourism_attractions.id = tourism_files.tourism_attraction_id
                    GROUP BY tourism_attractions.id
                """
            )
            tourism_attractions = cur.fetchall()

            # Get tourism_activities data
            cur.execute("""SELECT * FROM tourism_activities""")
            tourism_activities = cur.fetchall()

            attractions_df = pd.DataFrame(tourism_attractions)

            # Filter data based on hobbies
            if 'hobbies' in body:
                # Instantiate TfidfVectorizer class
                vectorizer_hobbies = TfidfVectorizer()

                random.shuffle(body['hobbies'])
                activities_df = pd.DataFrame(tourism_activities)
                activities_matrix = vectorizer_hobbies.fit_transform(
                    activities_df['name'].values.astype('U'))
                hobbies_matrix = vectorizer_hobbies.transform(
                    [body['hobbies'][0]])

                hobbies_similarity_scores = cosine_similarity(
                    hobbies_matrix, activities_matrix)
                rankings = hobbies_similarity_scores.argsort()[0][::-1][:20]

                attractions_df = attractions_df[attractions_df['id'].isin(
                    activities_df.loc[rankings, 'tourism_attraction_id'])]
                attractions_df = attractions_df.reset_index(drop=True)
            else:
                return jsonify({
                    'success': False,
                    'message': "hobbies doesn't exist"
                })

            if 'types' in body:
                # Instantiate TfidfVectorizer class
                vectorizer_description = TfidfVectorizer()
                vectorizer_types = TfidfVectorizer()

                types_matrix = vectorizer_types.fit_transform(
                    attractions_df['tourism_type_name'].values.astype('U'))
                types_input_matrix = vectorizer_types.transform(
                    [' '.join(body['types'])])
                types_similarity_scores = cosine_similarity(
                    types_input_matrix, types_matrix)

                descriptions_matrix = vectorizer_description.fit_transform(
                    attractions_df['descriptions'].values.astype('U'))
                types_input_matrix = vectorizer_description.transform(
                    [' '.join(body['types'])])
                descriptions_similarity_scores = cosine_similarity(
                    types_input_matrix, descriptions_matrix)

                combined_similarity_scores = (
                    0.5 * types_similarity_scores) + (0.5 * descriptions_similarity_scores)
                rankings = combined_similarity_scores.argsort()[0][::-1]
                attractions_df = attractions_df.loc[rankings]
            else:
                return jsonify({
                    'success': False,
                    'message': "types doesn't exist"
                })

            # Filter data based on budget_min
            if 'budget_min' in body:
                attractions_df = attractions_df[attractions_df['cost_from'].astype(
                    float) >= Decimal(body['budget_min'])]

            # Filter data based on budget_max
            if 'budget_max' in body:
                attractions_df = attractions_df[attractions_df['cost_to'].astype(
                    float) <= Decimal(body['budget_max'])]

            attractions_df['filename'] = attractions_df['filename'].str.split(
                ',').tolist()
            attractions_df['path'] = attractions_df['path'].str.split(
                ',').tolist()

            return jsonify({
                "success": True,
                "data": attractions_df.head().to_dict(orient='records'),
                "total": len(attractions_df.head())
            })
        except Exception as e:
            print(e)
            return jsonify({
                'success': False,
                'message': 'Invalid JSON'
            })
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid Content-Type'
        })
