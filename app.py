# Importando bibliotecas
import csv
from flask import Flask, request, jsonify, render_template, redirect
import random

app = Flask(__name__)

# Simulando um banco de dados de usuários e filmes
users = {}
movies = {}

# Carregando dados de usuários do arquivo CSV
with open('users.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        user_id = row[0]
        name = row[1]
        password = row[2]
        genre = row[3]
        users[name] = {'id': user_id, 'password': password, 'genre': genre}

# Carregando dados de filmes do arquivo CSV
with open('movies.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        movies[row['movieId']] = {'id': row['movieId'],
                                  'title': row['title'], 'genre': row['genres']}

# Simulando avaliações dos usuários
ratings = {}

# Rota principal da aplicação


@app.route('/')
def index():
    return render_template('index.html')

# Rota de registro de novos usuários


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        genre = request.form['genre']

        if name in users:
            return jsonify({'error': 'Username already exists'}), 400

        user_id = len(users) + 1
        users[name] = {'id': user_id, 'password': password, 'genre': genre}

        # Salvando dados de usuários no arquivo CSV
        with open('users.csv', 'a', newline='') as csvfile:
            fieldnames = ['id', 'name', 'password', 'genre']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'id': user_id, 'name': name,
                            'password': password, 'genre': genre})

        return redirect('/login')

    return render_template('register.html')

# Rota de autenticação de usuários registrados


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        if name in users and users[name]['password'] == password:
            return redirect(f'/recommendations?user_id={name}')
        else:
            return jsonify({'error': 'Invalid username or password'}), 401

    return render_template('login.html')

# Rota de recomendação dos filmes


@app.route('/recommendations')
def get_recommendations():
    user_id = request.args.get('user_id')
    if user_id not in users:
        return jsonify({'error': 'User not found'}), 404

    user_genre = users[user_id]['genre']
    user_ratings = ratings.get(user_id, {})

    # Filtragem colaborativa simples
    recommendations = []
    genre_recommendations = [movie_info for movie_id, movie_info in movies.items(
    ) if movie_info['genre'] == user_genre and movie_id not in user_ratings]

    # Selecionar aleatoriamente até 5 filmes do mesmo gênero
    selected_movies = random.sample(
        genre_recommendations, min(5, len(genre_recommendations)))

    for movie_info in selected_movies:
        recommendations.append({
            'title': movie_info['title'],
            'description': movie_info['genre']  # Adapte conforme necessário
        })

    # Renderiza diretamente a página HTML com as recomendações
    return render_template('recommendations.html', recommendations=recommendations)


if __name__ == '__main__':
    app.run(debug=True)
