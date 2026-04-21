"""SQLite access and domain queries."""

import datetime
import hashlib
import sqlite3
from typing import Dict, List, Optional

from .config import DB_PATH


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_output(output: str) -> str:
    normalized = output.strip().replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode()).hexdigest()


def get_problem_with_tests(problem_id: str) -> Optional[Dict]:
    """Get problem with all test cases"""
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM problems WHERE problem_id = ?", (problem_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        return None

    problem = {
        "problem_id": row["problem_id"],
        "title": row["title"] or "Untitled",
        "statement": row["statement"] or "",
        "time_limit": row["time_limit"] or 2.0,
        "memory_limit": row["memory_limit"] or 256,
        "difficulty": row["difficulty"] or "medium",
        "points": row["points"] or 100,
        "sample_input": row["sample_input"] or "",
        "sample_output": row["sample_output"] or "",
    }

    try:
        if "input_format" in row.keys():
            problem["input_format"] = row["input_format"] or ""
        if "output_format" in row.keys():
            problem["output_format"] = row["output_format"] or ""
        if "constraints" in row.keys():
            problem["constraints"] = row["constraints"] or ""
    except Exception:
        pass

    c.execute("""
        SELECT id, input_data, output_hash, is_sample, sample_output, points
        FROM test_cases WHERE problem_id = ?
        ORDER BY is_sample DESC, id
    """, (problem_id,))

    test_cases = []
    for tc_row in c.fetchall():
        tc = {
            "id": tc_row["id"],
            "input": tc_row["input_data"] or "",
            "input_data": tc_row["input_data"] or "",
            "output_hash": tc_row["output_hash"],
            "is_sample": bool(tc_row["is_sample"]),
            "points": tc_row["points"] or 0,
        }
        if tc_row["sample_output"]:
            tc["expected_output"] = tc_row["sample_output"]
        test_cases.append(tc)

    problem["test_cases"] = test_cases
    problem["test_count"] = len(test_cases)
    conn.close()

    return problem


def get_test_cases(problem_id: str) -> List[Dict]:
    """Get test cases for a problem (separate endpoint)"""
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        SELECT id, input_data, output_hash, is_sample, sample_output, points
        FROM test_cases WHERE problem_id = ?
        ORDER BY is_sample DESC, id
    """, (problem_id,))

    test_cases = []
    for tc_row in c.fetchall():
        tc = {
            "id": tc_row["id"],
            "input_data": tc_row["input_data"] or "",
            "output_hash": tc_row["output_hash"],
            "is_sample": bool(tc_row["is_sample"]),
            "points": tc_row["points"] or 0,
            "expected_output": tc_row["sample_output"] or "",
        }
        test_cases.append(tc)

    conn.close()
    return test_cases


def get_all_problems() -> List[Dict]:
    """Get all problems (basic info)"""
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT p.problem_id, p.title, p.time_limit, p.memory_limit,
               p.difficulty, p.points,
               (SELECT COUNT(*) FROM test_cases WHERE problem_id = p.problem_id) as test_count
        FROM problems p
        ORDER BY p.problem_id
    """)

    problems = []
    for row in c.fetchall():
        problems.append({
            "problem_id": row["problem_id"],
            "title": row["title"] or "Untitled",
            "time_limit": row["time_limit"] or 2.0,
            "memory_limit": row["memory_limit"] or 256,
            "difficulty": row["difficulty"] or "medium",
            "points": row["points"] or 100,
            "test_count": row["test_count"] or 0,
        })

    conn.close()
    return problems


def add_participant(user_id: str):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT OR IGNORE INTO participants (user_id, registered_at)
        VALUES (?, ?)
    """, (user_id, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()


def log_submission(
    user_id: str,
    problem_id: str,
    language: str,
    verdict: str,
    passed_tests: int,
    total_tests: int,
    execution_time: float,
):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO submissions
        (user_id, problem_id, language, verdict, passed_tests, total_tests, execution_time, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        problem_id,
        language,
        verdict,
        passed_tests,
        total_tests,
        execution_time,
        datetime.datetime.now().isoformat(),
    ))
    conn.commit()
    conn.close()


def get_scoreboard() -> List[Dict]:
    """Calculate scoreboard"""
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT penalty_time, start_time FROM contest_state WHERE id = 1")
    state_row = c.fetchone()
    penalty_minutes = state_row["penalty_time"] if state_row and state_row["penalty_time"] else 20
    start_time_str = state_row["start_time"] if state_row else None

    c.execute("""
        SELECT user_id, problem_id, verdict, timestamp
        FROM submissions
        ORDER BY timestamp
    """)
    submissions = c.fetchall()
    conn.close()

    user_data = {}

    for sub in submissions:
        user_id = sub["user_id"]
        problem_id = sub["problem_id"]
        verdict = sub["verdict"]
        timestamp = sub["timestamp"]

        if user_id not in user_data:
            user_data[user_id] = {"problems": {}, "total_penalty": 0, "total_solved": 0}

        if problem_id not in user_data[user_id]["problems"]:
            user_data[user_id]["problems"][problem_id] = {
                "solved": False,
                "attempts": 0,
                "time": 0,
            }

        prob = user_data[user_id]["problems"][problem_id]

        if not prob["solved"]:
            prob["attempts"] += 1

            if verdict == "Accepted":
                prob["solved"] = True
                user_data[user_id]["total_solved"] += 1

                if start_time_str:
                    try:
                        start = datetime.datetime.fromisoformat(start_time_str)
                        solve = datetime.datetime.fromisoformat(timestamp)
                        time_mins = int((solve - start).total_seconds() // 60)
                        penalty = (prob["attempts"] - 1) * penalty_minutes
                        user_data[user_id]["total_penalty"] += time_mins + penalty
                        prob["time"] = time_mins
                    except Exception:
                        pass

    leaderboard = []
    for user_id, data in user_data.items():
        leaderboard.append({
            "user_id": user_id,
            "problems_solved": data["total_solved"],
            "penalty": data["total_penalty"],
            "problems": data["problems"],
        })

    leaderboard.sort(key=lambda x: (-x["problems_solved"], x["penalty"]))

    for i, entry in enumerate(leaderboard):
        entry["rank"] = i + 1

    return leaderboard
