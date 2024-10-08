import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from database import SessionLocal, engine, Base
from models import Persona

# Cargar variables de entorno
load_dotenv()

# Iniciar la aplicación FastAPI
app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes especificar dominios permitidos en lugar de "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear las tablas si no existen
Base.metadata.create_all(bind=engine)

# Crear el esquema para validación de datos usando Pydantic
class PersonaSchema(BaseModel):
    nombre: str
    apellido: str
    email: str

    class Config:
        from_attributes = True

# Dependency para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ruta para obtener todas las personas o una en particular
@app.get("/personas/{persona_id}", response_model=PersonaSchema)
def get_persona(persona_id: int, db: Session = Depends(get_db)):
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona

@app.get("/personas", response_model=list[PersonaSchema])
def get_personas(db: Session = Depends(get_db)):
    personas = db.query(Persona).all()
    return personas

# Ruta para crear una nueva persona
@app.post("/personas", response_model=PersonaSchema)
def create_persona(persona: PersonaSchema, db: Session = Depends(get_db)):
    new_persona = Persona(nombre=persona.nombre, apellido=persona.apellido, email=persona.email)
    db.add(new_persona)
    db.commit()
    db.refresh(new_persona)
    return new_persona

# Ruta para actualizar una persona
@app.put("/personas/{persona_id}", response_model=PersonaSchema)
def update_persona(persona_id: int, persona: PersonaSchema, db: Session = Depends(get_db)):
    existing_persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not existing_persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    existing_persona.nombre = persona.nombre
    existing_persona.apellido = persona.apellido
    existing_persona.email = persona.email
    db.commit()
    db.refresh(existing_persona)
    return existing_persona

# Ruta para eliminar una persona
@app.delete("/personas/{persona_id}")
def delete_persona(persona_id: int, db: Session = Depends(get_db)):
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    db.delete(persona)
    db.commit()
    return {"message": "Persona deleted successfully"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5555, debug=True)
