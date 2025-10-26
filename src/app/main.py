from __future__ import annotations

import logging
import math
from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

# Logs lisibles
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

app = FastAPI(title="Arithmetic API", version="1.0.0")


class Operands(BaseModel):
    a: float
    b: float

    @field_validator("a", "b")
    @classmethod
    def must_be_finite(cls, v: float) -> float:
        if not math.isfinite(v):
            raise ValueError("La valeur doit être un nombre fini (ni NaN ni infini).")
        return v


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


def _result_payload(value: float) -> Dict[str, float]:
    return {"result": value}


@app.post("/add")
def add(payload: Operands) -> Dict[str, float]:
    logging.info("Addition: %s + %s", payload.a, payload.b)
    return _result_payload(payload.a + payload.b)


@app.post("/sub")
def sub(payload: Operands) -> Dict[str, float]:
    logging.info("Soustraction: %s - %s", payload.a, payload.b)
    return _result_payload(payload.a - payload.b)


@app.post("/mul")
def mul(payload: Operands) -> Dict[str, float]:
    logging.info("Multiplication: %s * %s", payload.a, payload.b)
    return _result_payload(payload.a * payload.b)


@app.post("/div")
def div(payload: Operands) -> Dict[str, float]:
    logging.info("Division: %s / %s", payload.a, payload.b)
    if payload.b == 0:
        raise HTTPException(
            status_code=400,
            detail="Division par zéro interdite (paramètre 'b' ne doit pas être égal à 0).",
        )
    return _result_payload(payload.a / payload.b)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app.main:app", host="0.0.0.0", port=8000, reload=False)
