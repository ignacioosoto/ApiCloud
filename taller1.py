from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# ---------------------------
# Configuración de la Base de Datos (SQLite)
# ---------------------------
DATABASE_URL = "sqlite:///./items.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ---------------------------
# Modelo de la tabla
# ---------------------------
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)


# Crear las tablas en la BD
Base.metadata.create_all(bind=engine)


# ---------------------------
# Dependencia para obtener sesión
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------
# Inicializar FastAPI
# ---------------------------
app = FastAPI(title="CRUD API con FastAPI", version="1.0")


# ---------------------------
# Rutas CRUD
# ---------------------------

# CREATE
@app.post("/items/", response_model=dict)
def create_item(name: str, description: str, db: Session = Depends(get_db)):
    item = Item(name=name, description=description)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"message": "Item creado con éxito", "item": {"id": item.id, "name": item.name, "description": item.description}}


# READ (Obtener todos)
@app.get("/items/", response_model=list)
def read_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return [{"id": i.id, "name": i.name, "description": i.description} for i in items]


# READ (Obtener por ID)
@app.get("/items/{item_id}", response_model=dict)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return {"id": item.id, "name": item.name, "description": item.description}


# UPDATE
@app.put("/items/{item_id}", response_model=dict)
def update_item(item_id: int, name: str, description: str, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")

    item.name = name
    item.description = description
    db.commit()
    db.refresh(item)
    return {"message": "Item actualizado", "item": {"id": item.id, "name": item.name, "description": item.description}}


# DELETE
@app.delete("/items/{item_id}", response_model=dict)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")

    db.delete(item)
    db.commit()
    return {"message": "Item eliminado con éxito"}
