from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    # เปลี่ยนชื่อฐานข้อมูลเป็น moviestore.db
    conn = sqlite3.connect("moviestore.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    # เปลี่ยนตารางหมวดหมู่เป็น genres
    conn.execute("""
    CREATE TABLE IF NOT EXISTS genres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)
    # เปลี่ยนตารางสินค้าเป็น movies
    conn.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        price REAL,
        poster TEXT,
        stock INTEGER DEFAULT 0,
        genre_id INTEGER,
        FOREIGN KEY (genre_id) REFERENCES genres (id)
    )
    """)
    # เพิ่มแนวหนังเริ่มต้น
    default_genres = ["Action", "Sci-Fi", "Horror", "Comedy", "Drama"]
    for gen in default_genres:
        try:
            conn.execute("INSERT INTO genres (name) VALUES (?)", (gen,))
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    conn = get_db()
    movies = conn.execute("""
        SELECT movies.*, genres.name as genre_name 
        FROM movies 
        LEFT JOIN genres ON movies.genre_id = genres.id
    """).fetchall()
    conn.close()
    return render_template("cakemenu.html", movies=movies)

@app.route("/append", methods=["GET", "POST"])
def append():
    conn = get_db()
    genres = conn.execute("SELECT * FROM genres").fetchall()
    if request.method == "POST":
        title = request.form["title"]
        price = request.form["price"]
        poster = request.form["poster"]
        stock = request.form.get("stock", "0")
        genre_id = request.form.get("genre_id")
        
        conn.execute("INSERT INTO movies (title, price, poster, stock, genre_id) VALUES (?, ?, ?, ?, ?)",
                     (title, price, poster, stock, genre_id))
        conn.commit()
        conn.close()
        return redirect("/")
    return render_template("append.html", genres=genres)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()
    genres = conn.execute("SELECT * FROM genres").fetchall()
    if request.method == "POST":
        title = request.form["title"]
        price = request.form["price"]
        poster = request.form["poster"]
        stock = request.form["stock"]
        genre_id = request.form["genre_id"]
        
        conn.execute("UPDATE movies SET title=?, price=?, poster=?, stock=?, genre_id=? WHERE id=?",
                     (title, price, poster, stock, genre_id, id))
        conn.commit()
        conn.close()
        return redirect("/")
    
    movie = conn.execute("SELECT * FROM movies WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("edit.html", movie=movie, genres=genres)

@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM movies WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)