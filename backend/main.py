from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Chatbot PGN – API",
    description="API de referencia en Python para el Chatbot PGN (horarios, sedes y denuncias).",
    version="1.0.0"
)

# CORS
origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Base de datos (SQLite por defecto)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pgn_chatbot.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Denuncia(Base):
    __tablename__ = "denuncias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    dpi = Column(String(30), nullable=True)
    telefono = Column(String(30), nullable=True)
    departamento = Column(String(60), nullable=True)
    tipo = Column(String(80), nullable=False)
    descripcion = Column(Text, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class RespuestaSimple(BaseModel):
    status: str = "ok"
    respuesta: str

class DenunciaIn(BaseModel):
    nombre: str = Field(...)
    dpi: Optional[str] = None
    telefono: Optional[str] = None
    departamento: Optional[str] = None
    tipo: str = Field(...)
    descripcion: str = Field(...)

class DenunciaOut(BaseModel):
    status: str
    id: int
    mensaje: str

class Sede(BaseModel):
    departamento: str
    nombre_sede: str
    direccion: str
    telefono: Optional[str] = None
    horario: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

class SedesResponse(BaseModel):
    status: str = "ok"
    sedes: List[Sede]

class ChatIn(BaseModel):
    mensaje: str

class ChatOut(BaseModel):
    status: str = "ok"
    intent_detectado: str
    respuesta: str

SEDES = [
    {"departamento":"Guatemala","nombre_sede":"Sede Central PGN","direccion":"Zona 1, Ciudad de Guatemala","telefono":"1234-5678","horario":"Lunes a viernes de 8:00 a 16:00","lat":14.6349,"lng":-90.5069},
    {"departamento":"Quetzaltenango","nombre_sede":"Sede PGN Quetzaltenango","direccion":"Zona 3, Quetzaltenango","telefono":"7766-1122","horario":"Lunes a viernes de 8:00 a 16:00","lat":14.8347,"lng":-91.5180},
    {"departamento":"Huehuetenango","nombre_sede":"Sede PGN Huehuetenango","direccion":"Zona 1, Huehuetenango","telefono":"7765-0099","horario":"Lunes a viernes de 8:00 a 16:00","lat":15.3190,"lng":-91.4700},
]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

HORARIO_OFICIAL = "La PGN atiende de lunes a viernes de 8:00 a 16:00 horas."

def detectar_intent(mensaje: str) -> str:
    msg = mensaje.lower()
    if any(k in msg for k in ["horario","horarios","atención","atienden","abren","abierto","cierra"]):
        return "consulta_horarios"
    if any(k in msg for k in ["sede","sedes","ubicación","ubicacion","direccion","dirección","departamento","mapa","dónde","donde"]):
        return "ubicacion_sedes"
    if any(k in msg for k in ["denuncia","denunciar","maltrato","violencia","abuso","reportar","presentar"]):
        return "denuncia_preliminar"
    return "desconocido"

@app.get("/api/horarios", response_model=RespuestaSimple)
def obtener_horarios():
    return {"status": "ok", "respuesta": HORARIO_OFICIAL}

@app.get("/api/sedes", response_model=SedesResponse)
def obtener_sedes(departamento: Optional[str] = Query(None)):
    if departamento:
        filtradas = [Sede(**s) for s in SEDES if s["departamento"].lower() == departamento.lower()]
    else:
        filtradas = [Sede(**s) for s in SEDES]
    return {"status": "ok", "sedes": filtradas}

@app.post("/api/denuncias", response_model=DenunciaOut)
def crear_denuncia(payload: DenunciaIn):
    db = next(get_db())
    registro = Denuncia(
        nombre=payload.nombre, dpi=payload.dpi, telefono=payload.telefono,
        departamento=payload.departamento, tipo=payload.tipo, descripcion=payload.descripcion
    )
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return {"status": "ok", "id": registro.id,
            "mensaje":"Su denuncia preliminar fue registrada. Un operador de la PGN revisará la información."}

@app.post("/api/chat", response_model=ChatOut)
def chat_router(entrada: ChatIn):
    intent = detectar_intent(entrada.mensaje)
    if intent == "consulta_horarios":
        return {"status":"ok","intent_detectado":intent,"respuesta":HORARIO_OFICIAL}
    if intent == "ubicacion_sedes":
        hint = "Puedes pedir: 'Sedes en Guatemala', 'Ubicación sedes Quetzaltenango'."
        return {"status":"ok","intent_detectado":intent,"respuesta":f"Tengo {len(SEDES)} sedes registradas. {hint} También: /api/sedes?departamento=Guatemala"}
    if intent == "denuncia_preliminar":
        ejemplo = {"nombre":"Juan Pérez","dpi":"1234567890101","telefono":"5555-5555","departamento":"Guatemala","tipo":"violencia","descripcion":"Descripción breve..."}
        return {"status":"ok","intent_detectado":intent,"respuesta":f"Envía POST a /api/denuncias con JSON similar a: {ejemplo}"}
    return {"status":"ok","intent_detectado":"desconocido","respuesta":"No pude reconocer tu solicitud. Puedo ayudarte con: horarios, sedes y denuncias."}
