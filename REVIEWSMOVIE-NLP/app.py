from flask import Flask, render_template, request, url_for, redirect, flash
import pickle
import random

app = Flask(__name__)
app.secret_key = "supersecretkey" # Dibutuhkan untuk fitur 'flash' message

# 1. LOAD MODEL & VECTORIZER
# Pastikan file model_sentimen.pkl dan vectorizer.pkl ada di folder yang sama
try:
    model = pickle.load(open('model_sentimen.pkl', 'rb'))
    vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))
except Exception as e:
    print(f"Warning: Model tidak ditemukan atau error: {e}")
    model = None
    vectorizer = None

# 2. DATA BANK FILM (30 FILM) - SUDAH DIPERBAIKI
bank_film = [
    {"id": 1, "judul": "Interstellar", "img": "interstellar.jpg"},
    {"id": 2, "judul": "Spider-Man: No Way Home", "img": "spiderman.jpg"},
    {"id": 3, "judul": "Joker", "img": "joker.jpg"},
    {"id": 4, "judul": "The Dark Knight", "img": "darkknight.jpg"},
    {"id": 5, "judul": "Avengers: Endgame", "img": "avengers.jpg"},
    {"id": 6, "judul": "Inception", "img": "inception.jpg"},
    {"id": 7, "judul": "Titanic", "img": "titanic.jpg"},
    {"id": 8, "judul": "Encanto", "img": "encanto.jpg"},
    {"id": 9, "judul": "Frozen", "img": "frozen.jpg"},
    {"id": 10, "judul": "Hulk", "img": "hulk.jpg"},
    {"id": 11, "judul": "Madagascar", "img": "madagascar.jpg"},
    {"id": 12, "judul": "Minions", "img": "minions.jpg"},
    {"id": 13, "judul": "Moana", "img": "moana.jpg"},
    {"id": 14, "judul": "Mulan", "img": "mulan.jpg"},
    {"id": 15, "judul": "Nemo", "img": "nemo.jpg"},
    {"id": 16, "judul": "The Lion King", "img": "lion_king.jpg"},
    {"id": 17, "judul": "Shrek", "img": "shrek.jpg"},
    {"id": 18, "judul": "Iron Man", "img": "iron_man.jpg"},
    {"id": 19, "judul": "Black Panther", "img": "black_panther.jpg"},
    {"id": 20, "judul": "Up", "img": "up.jpg"},
    {"id": 21, "judul": "Zootopia", "img": "zootopia.jpg"},
    {"id": 22, "judul": "Coco", "img": "coco.jpg"},
    {"id": 23, "judul": "Toy Story", "img": "toy_story.jpg"},
    {"id": 24, "judul": "Despicable Me", "img": "despicableme.jpg"},
    {"id": 25, "judul": "Doctor Strange", "img": "doctorstrange.jpg"},
    {"id": 26, "judul": "The Batman", "img": "the_batman.jpg"},
    {"id": 27, "judul": "Captain America", "img": "captainamerica.jpg"},
    {"id": 28, "judul": "Aladdin", "img": "aladdin.jpg"},
    {"id": 29, "judul": "Dune", "img": "dune.jpg"},
    {"id": 30, "judul": "Barbie", "img": "barbie.jpg"}
]

# SIMPAN FAVORIT DI MEMORI (Bersifat sementara saat server jalan)
my_movies = []

# --- ROUTES ---

@app.route('/')
def index():
    # Menampilkan 5 film acak di dashboard utama
    tampil_film = random.sample(bank_film, 5)
    return render_template('index.html', films=tampil_film)

@app.route('/movie/<int:film_id>')
def movie_detail(film_id):
    # Mengambil detail film berdasarkan ID
    film = next((f for f in bank_film if f['id'] == film_id), None)
    if film:
        return render_template('review.html', film=film)
    return redirect(url_for('index'))

@app.route('/predict/<int:film_id>', methods=['POST'])
def predict(film_id):
    film = next((f for f in bank_film if f['id'] == film_id), None)
    review_user = request.form['review']
    review_clean = review_user.lower()
    
    # 1. Pengecekan manual kata kunci (Keyword Match)
    # Menambahkan kata 'funny', 'enjoyed', 'like' dll agar lebih akurat
    kata_positif = [
        'good', 'amazing', 'best', 'slay', 'keren', 'bagus', 'love', 
        'funny', 'enjoyed', 'like', 'perfect', 'masterpiece', 'recommended',
        'seru', 'asik', 'mantap', 'cakep', 'indah'
    ]
    
    if any(kata in review_clean for kata in kata_positif):
        label = "POSITIF"
    else:
        # 2. Jika tidak ada kata kunci, gunakan Model AI
        if model and vectorizer:
            try:
                teks_vektor = vectorizer.transform([review_user])
                hasil = model.predict(teks_vektor)[0]
                label = "POSITIF" if hasil == 'pos' else "NEGATIF"
            except:
                label = "NEGATIF"
        else:
            label = "NEGATIF"
    
    return render_template('review.html', film=film, prediction=label, original_text=review_user)

@app.route('/add_favorite/<int:film_id>')
def add_favorite(film_id):
    film = next((f for f in bank_film if f['id'] == film_id), None)
    # Tambahkan ke favorit jika film ada dan belum ada di list favorit
    if film and film not in my_movies:
        my_movies.append(film)
        flash(f"{film['judul']} added to favorites! 🎀")
    return redirect(url_for('my_movies_page'))

@app.route('/my-movies')
def my_movies_page():
    # Menampilkan halaman koleksi film favorit user
    return render_template('my_movies.html', films=my_movies)

@app.route('/analytics')
def analytics():
    # Menghitung persentase "aesthetic" berdasarkan jumlah favorit
    # Kita buat angka dinamis biar keren
    persentase_positif = "88%" if len(my_movies) == 0 else f"{min(90 + len(my_movies), 99)}%"
    
    stats = {
        "total": len(bank_film), 
        "fav_count": len(my_movies), 
        "vibe_score": persentase_positif, # Ini untuk Positive Vibes
        "trending": "Spider-Man", 
        "status": "Active 🔥"             # Ini untuk Community Status
    }
    return render_template('analytics.html', stats=stats)

if __name__ == '__main__':
    import os
    # Railway akan ngasih port lewat environment variable
    port = int(os.environ.get("PORT", 5000))
    # host='0.0.0.0' wajib biar bisa diakses publik
    app.run(host='0.0.0.0', port=port)