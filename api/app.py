from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from strawberry.flask.views import GraphQLView
from schema import schema
from models import SessionLocal, Game as GameModel, Tag as TagModel

app = Flask(__name__)
CORS(app)

# FRONTEND
@app.route("/")
def home():
    return render_template("index.html")

# GRAPHQL
app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql_view", schema=schema),
)

# API GAMES
@app.route("/api/games")
def rest_games():
    session = SessionLocal()

    try:
        q = session.query(GameModel)

        title = request.args.get("title")
        platform = request.args.get("platform")
        genre = request.args.get("genre")
        tag = request.args.get("tag")

        limit = int(request.args.get("limit", 20))
        offset = int(request.args.get("offset", 0))

        if title:
            q = q.filter(GameModel.title.ilike(f"%{title}%"))

        if platform:
            q = q.filter(GameModel.platform.ilike(f"%{platform}%"))

        if genre:
            q = q.filter(GameModel.genre.ilike(f"%{genre}%"))

        if tag:
            q = q.join(GameModel.tags).filter(
                TagModel.name.ilike(f"%{tag}%")
            )

        total = q.count()

        games = q.offset(offset).limit(limit).all()

        return jsonify({
            "total": total,
            "limit": limit,
            "offset": offset,

            "results": [
                {
                    "id": g.id,
                    "title": g.title,
                    "thumbnail": g.thumbnail,
                    "short_description": g.short_description,
                    "genre": g.genre,
                    "platform": g.platform,
                    "publisher": g.publisher,
                    "developer": g.developer,
                    "release_date": str(g.release_date) if g.release_date else None,
                    "price": g.price,
                    "game_url": g.game_url,
                    "tags": [t.name for t in g.tags],
                }

                for g in games
            ]
        })

    finally:
        session.close()

# GAME POR ID
@app.route("/api/games/<int:game_id>")
def rest_game(game_id):

    session = SessionLocal()

    try:
        g = session.query(GameModel).filter_by(id=game_id).first()

        if not g:
            return jsonify({
                "error": "Juego no encontrado"
            }), 404

        return jsonify({
            "id": g.id,
            "title": g.title,
            "thumbnail": g.thumbnail,
            "short_description": g.short_description,
            "genre": g.genre,
            "platform": g.platform,
            "publisher": g.publisher,
            "developer": g.developer,
            "release_date": str(g.release_date) if g.release_date else None,
            "price": g.price,
            "game_url": g.game_url,
            "tags": [t.name for t in g.tags],
        })

    finally:
        session.close()

# PLATFORMS
@app.route("/api/platforms")
def rest_platforms():

    session = SessionLocal()

    try:
        rows = session.query(GameModel.platform).distinct().all()

        return jsonify(
            sorted([r[0] for r in rows if r[0]])
        )

    finally:
        session.close()

# GENRES
@app.route("/api/genres")
def rest_genres():

    session = SessionLocal()

    try:
        rows = session.query(GameModel.genre).distinct().all()

        return jsonify(
            sorted([r[0] for r in rows if r[0]])
        )

    finally:
        session.close()

# TAGS
@app.route("/api/tags")
def rest_tags():

    session = SessionLocal()

    try:
        tags = session.query(TagModel).order_by(TagModel.name).all()

        return jsonify([
            {
                "id": t.id,
                "name": t.name
            }

            for t in tags
        ])

    finally:
        session.close()

# HEALTH
@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok"
    })

# MAIN
if __name__ == "__main__":


    print("🚀 Flask corriendo en puerto 5000...")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )