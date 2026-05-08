import strawberry
from typing import Optional, List
from models import SessionLocal, Game as GameModel, Tag as TagModel

@strawberry.type
class TagType:
    id:   int
    name: str

@strawberry.type
class GameType:
    id:                int
    title:             str
    thumbnail:         Optional[str]
    short_description: Optional[str]
    game_url:          Optional[str]
    genre:             Optional[str]
    platform:          Optional[str]
    publisher:         Optional[str]
    developer:         Optional[str]
    release_date:      Optional[str]
    price:             Optional[str]
    tags:              List[TagType]

def to_type(g: GameModel) -> GameType:
    return GameType(
        id=g.id, title=g.title,
        thumbnail=g.thumbnail,
        short_description=g.short_description,
        game_url=g.game_url,
        genre=g.genre, platform=g.platform,
        publisher=g.publisher, developer=g.developer,
        release_date=str(g.release_date) if g.release_date else None,
        price=g.price,
        tags=[TagType(id=t.id, name=t.name) for t in g.tags],
    )

@strawberry.type
class Query:

    @strawberry.field
    def games(
        self,
        title:    Optional[str] = None,
        platform: Optional[str] = None,
        genre:    Optional[str] = None,
        tag:      Optional[str] = None,
        limit:    Optional[int] = 20,
        offset:   Optional[int] = 0,
    ) -> List[GameType]:
        session = SessionLocal()
        try:
            q = session.query(GameModel)
            if title:    q = q.filter(GameModel.title.ilike(f"%{title}%"))
            if platform: q = q.filter(GameModel.platform.ilike(f"%{platform}%"))
            if genre:    q = q.filter(GameModel.genre.ilike(f"%{genre}%"))
            if tag:      q = q.join(GameModel.tags).filter(TagModel.name.ilike(f"%{tag}%"))
            return [to_type(g) for g in q.offset(offset).limit(limit).all()]
        finally:
            session.close()

    @strawberry.field
    def game(self, id: int) -> Optional[GameType]:
        session = SessionLocal()
        try:
            g = session.query(GameModel).filter_by(id=id).first()
            return to_type(g) if g else None
        finally:
            session.close()

    @strawberry.field
    def tags(self) -> List[TagType]:
        session = SessionLocal()
        try:
            return [TagType(id=t.id, name=t.name)
                    for t in session.query(TagModel).order_by(TagModel.name).all()]
        finally:
            session.close()

    @strawberry.field
    def platforms(self) -> List[str]:
        session = SessionLocal()
        try:
            rows = session.query(GameModel.platform).distinct().all()
            return sorted([r[0] for r in rows if r[0]])
        finally:
            session.close()

    @strawberry.field
    def genres(self) -> List[str]:
        session = SessionLocal()
        try:
            rows = session.query(GameModel.genre).distinct().all()
            return sorted([r[0] for r in rows if r[0]])
        finally:
            session.close()

    @strawberry.field
    def games_count(self) -> int:
        session = SessionLocal()
        try:
            return session.query(GameModel).count()
        finally:
            session.close()

schema = strawberry.Schema(query=Query)