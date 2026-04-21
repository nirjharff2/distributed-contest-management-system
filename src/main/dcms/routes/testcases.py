"""Test case endpoints."""

from fastapi import APIRouter, HTTPException

from ..database import get_db, get_test_cases, hash_output
from ..models import TestCaseCreate

router = APIRouter()


@router.get("/problems/{problem_id}/testcases")
async def get_problem_testcases(problem_id: str):
    """Get all test cases for a problem"""
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT 1 FROM problems WHERE problem_id = ?", (problem_id,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Problem not found")

    test_cases = get_test_cases(problem_id)
    conn.close()

    return {"testcases": test_cases, "count": len(test_cases)}


@router.post("/problems/{problem_id}/testcases")
async def add_test_case(problem_id: str, test_case: TestCaseCreate):
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT 1 FROM problems WHERE problem_id = ?", (problem_id,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Problem not found")

    output_hash = hash_output(test_case.expected_output)
    sample_output = test_case.expected_output if test_case.is_sample else ""

    c.execute("""
        INSERT INTO test_cases
        (problem_id, input_data, output_hash, is_sample, sample_output, points)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        problem_id,
        test_case.input_data,
        output_hash,
        1 if test_case.is_sample else 0,
        sample_output,
        test_case.points,
    ))

    tc_id = c.lastrowid
    conn.commit()
    conn.close()

    return {"status": "Test case added", "id": tc_id}


@router.delete("/problems/{problem_id}/testcases/{testcase_id}")
async def delete_test_case(problem_id: str, testcase_id: int):
    """Delete a specific test case"""
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        SELECT 1 FROM test_cases
        WHERE id = ? AND problem_id = ?
    """, (testcase_id, problem_id))

    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Test case not found")

    c.execute("DELETE FROM test_cases WHERE id = ?", (testcase_id,))
    conn.commit()
    conn.close()

    return {"status": "Test case deleted", "id": testcase_id}


@router.delete("/testcases/{testcase_id}")
async def delete_test_case_direct(testcase_id: int):
    """Delete a test case by ID directly"""
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT 1 FROM test_cases WHERE id = ?", (testcase_id,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Test case not found")

    c.execute("DELETE FROM test_cases WHERE id = ?", (testcase_id,))
    conn.commit()
    conn.close()

    return {"status": "Test case deleted", "id": testcase_id}
