"""Problem CRUD."""

import datetime
import sqlite3

from fastapi import APIRouter, HTTPException

from .. import state
from ..broadcast import broadcast_problem, broadcast_to_all
from ..database import (
    get_db,
    get_problem_with_tests,
    get_all_problems,
    hash_output,
)
from ..models import ProblemCreate, ProblemUpdate

router = APIRouter()


@router.get("/problems")
async def list_problems():
    return {"problems": get_all_problems()}


@router.get("/problems/{problem_id}")
async def get_problem(problem_id: str):
    problem = get_problem_with_tests(problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return {"problem": problem}


@router.post("/problems")
async def create_problem(problem: ProblemCreate):
    conn = get_db()
    c = conn.cursor()

    try:
        c.execute("PRAGMA table_info(problems)")
        columns = [col[1] for col in c.fetchall()]

        if "input_format" in columns:
            c.execute("""
                INSERT INTO problems
                (problem_id, title, statement, time_limit, memory_limit,
                 difficulty, points, sample_input, sample_output,
                 input_format, output_format, constraints, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                problem.problem_id,
                problem.title,
                problem.statement,
                problem.time_limit,
                problem.memory_limit,
                problem.difficulty,
                problem.points,
                problem.sample_input,
                problem.sample_output,
                problem.input_format,
                problem.output_format,
                problem.constraints,
                datetime.datetime.now().isoformat(),
            ))
        else:
            c.execute("""
                INSERT INTO problems
                (problem_id, title, statement, time_limit, memory_limit,
                 difficulty, points, sample_input, sample_output, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                problem.problem_id,
                problem.title,
                problem.statement,
                problem.time_limit,
                problem.memory_limit,
                problem.difficulty,
                problem.points,
                problem.sample_input,
                problem.sample_output,
                datetime.datetime.now().isoformat(),
            ))

        if problem.sample_output:
            output_hash = hash_output(problem.sample_output)
            c.execute("""
                INSERT INTO test_cases
                (problem_id, input_data, output_hash, is_sample, sample_output, points)
                VALUES (?, ?, ?, 1, ?, ?)
            """, (
                problem.problem_id,
                problem.sample_input,
                output_hash,
                problem.sample_output,
                problem.points,
            ))

        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Problem ID already exists")

    conn.close()
    return {"status": "Problem created", "problem_id": problem.problem_id}


@router.put("/problems/{problem_id}")
async def update_problem(problem_id: str, update: ProblemUpdate):
    """Update an existing problem"""
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT 1 FROM problems WHERE problem_id = ?", (problem_id,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Problem not found")

    updates = []
    values = []

    if update.title is not None:
        updates.append("title = ?")
        values.append(update.title)
    if update.statement is not None:
        updates.append("statement = ?")
        values.append(update.statement)
    if update.time_limit is not None:
        updates.append("time_limit = ?")
        values.append(update.time_limit)
    if update.memory_limit is not None:
        updates.append("memory_limit = ?")
        values.append(update.memory_limit)
    if update.difficulty is not None:
        updates.append("difficulty = ?")
        values.append(update.difficulty)
    if update.points is not None:
        updates.append("points = ?")
        values.append(update.points)
    if update.sample_input is not None:
        updates.append("sample_input = ?")
        values.append(update.sample_input)
    if update.sample_output is not None:
        updates.append("sample_output = ?")
        values.append(update.sample_output)

    if updates:
        values.append(problem_id)
        query = f"UPDATE problems SET {', '.join(updates)} WHERE problem_id = ?"
        c.execute(query, values)
        conn.commit()

    conn.close()
    return {"status": "Problem updated", "problem_id": problem_id}


@router.delete("/problems/{problem_id}")
async def delete_problem(problem_id: str):
    """Delete a problem and its test cases"""
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT 1 FROM problems WHERE problem_id = ?", (problem_id,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Problem not found")

    try:
        c.execute("DELETE FROM test_cases WHERE problem_id = ?", (problem_id,))
        c.execute("DELETE FROM problems WHERE problem_id = ?", (problem_id,))

        conn.commit()
        print(f"🗑️ Deleted problem: {problem_id}")

    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Failed to delete problem: {str(e)}")

    conn.close()

    await broadcast_to_all({
        "type": "PROBLEM_DELETED",
        "problem_id": problem_id,
    })

    return {"status": "Problem deleted", "problem_id": problem_id}


@router.get("/send_problem/{problem_id}")
async def send_problem_to_clients(problem_id: str):
    problem = get_problem_with_tests(problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    await broadcast_problem(problem_id)
    return {"status": "Problem sent", "problem_id": problem_id, "clients": len(state.clients)}
