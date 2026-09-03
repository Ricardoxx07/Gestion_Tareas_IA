from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from models.usuario import Usuario
from models.usuario_db import UsuarioDB
from repository.usuario_repository_interface import UsuarioRepositoryInterface


class UsuarioRepositoryDB(UsuarioRepositoryInterface):

    def __init__(self, db: Session):
        self.db = db

    def obtener_por_id(self, id_usuario: int) -> Usuario | None:
        usuario_db = self.db.get(UsuarioDB, id_usuario)

        if usuario_db is None:
            return None

        return Usuario(
            id=usuario_db.id,
            email=usuario_db.email,
            password_hash=usuario_db.password_hash
        )

    def obtener_por_email(self, email: str) -> Usuario | None:
        usuario_db = (
            self.db.query(UsuarioDB)
            .filter(UsuarioDB.email == email)
            .first()
        )

        if usuario_db is None:
            return None

        return Usuario(
            id=usuario_db.id,
            email=usuario_db.email,
            password_hash=usuario_db.password_hash
        )

    def guardar_usuario(self, usuario: Usuario) -> Usuario:
        usuario_db = UsuarioDB(
            email=usuario.email,
            password_hash=usuario.password_hash
        )

        try:
            self.db.add(usuario_db)
            self.db.commit()
            self.db.refresh(usuario_db)
        except SQLAlchemyError:
            self.db.rollback()
            raise

        return Usuario(
            id=usuario_db.id,
            email=usuario_db.email,
            password_hash=usuario_db.password_hash
        )
