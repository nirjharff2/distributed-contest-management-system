"""
Database setup for DCMS - Complete Reset Version
"""
import sqlite3
import os
from datetime import datetime

from dcms.config import DB_PATH
from dcms.database import hash_output


def setup_database(reset=False):
    """Initialize the database with all tables"""
    
    if reset and os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"🗑️  Deleted old database")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Participants table
    c.execute("""
    CREATE TABLE IF NOT EXISTS participants (
        user_id TEXT PRIMARY KEY,
        name TEXT DEFAULT '',
        email TEXT DEFAULT '',
        registered_at TEXT
    )
    """)

    # Problems table
    c.execute("""
    CREATE TABLE IF NOT EXISTS problems (
        problem_id TEXT PRIMARY KEY,
        title TEXT NOT NULL DEFAULT 'Untitled',
        statement TEXT DEFAULT '',
        time_limit REAL DEFAULT 2.0,
        memory_limit INTEGER DEFAULT 256,
        difficulty TEXT DEFAULT 'medium',
        points INTEGER DEFAULT 100,
        sample_input TEXT DEFAULT '',
        sample_output TEXT DEFAULT '',
        created_at TEXT
    )
    """)

    # Test cases table
    c.execute("""
    CREATE TABLE IF NOT EXISTS test_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        problem_id TEXT NOT NULL,
        input_data TEXT DEFAULT '',
        output_hash TEXT NOT NULL,
        is_sample INTEGER DEFAULT 0,
        sample_output TEXT DEFAULT '',
        points INTEGER DEFAULT 0,
        FOREIGN KEY (problem_id) REFERENCES problems(problem_id) ON DELETE CASCADE
    )
    """)

    # Submissions table
    c.execute("""
    CREATE TABLE IF NOT EXISTS submissions (
        submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        problem_id TEXT NOT NULL,
        language TEXT DEFAULT 'python',
        verdict TEXT DEFAULT 'Pending',
        passed_tests INTEGER DEFAULT 0,
        total_tests INTEGER DEFAULT 0,
        execution_time REAL DEFAULT 0,
        timestamp TEXT,
        FOREIGN KEY (user_id) REFERENCES participants(user_id),
        FOREIGN KEY (problem_id) REFERENCES problems(problem_id)
    )
    """)

    # Contest state table
    c.execute("""
    CREATE TABLE IF NOT EXISTS contest_state (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        active INTEGER DEFAULT 0,
        start_time TEXT,
        end_time TEXT,
        penalty_time INTEGER DEFAULT 20,
        title TEXT DEFAULT 'Programming Contest'
    )
    """)

    # Announcements table
    c.execute("""
    CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL DEFAULT 'Announcement',
        content TEXT DEFAULT '',
        priority TEXT DEFAULT 'normal',
        created_at TEXT
    )
    """)

    # Initialize contest state
    c.execute("INSERT OR IGNORE INTO contest_state (id, active, penalty_time) VALUES (1, 0, 20)")

    conn.commit()
    conn.close()
    print("✅ Database setup completed!")


def add_sample_problems():
    """Add sample problems for testing"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()

    problems = [
        {
            "problem_id": "A",
            "title": "Hello World",
            "statement": """Print "Hello, World!" to the console.

Your output should be exactly: Hello, World!

Note: Pay attention to capitalization, spacing, and punctuation.""",
            "time_limit": 1.0,
            "memory_limit": 128,
            "difficulty": "easy",
            "points": 50,
            "sample_input": "",
            "sample_output": "Hello, World!",
            "test_cases": [
                {"input": "", "output": "Hello, World!", "is_sample": True, "points": 50}
            ]
        },
        {
            "problem_id": "B",
            "title": "Sum of Two Numbers",
            "statement": """Given two integers A and B, output their sum.

Input:
Two space-separated integers A and B (-10^9 ≤ A, B ≤ 10^9)

Output:
A single integer: the sum of A and B

Example:
Input: 3 5
Output: 8""",
            "time_limit": 1.0,
            "memory_limit": 128,
            "difficulty": "easy",
            "points": 100,
            "sample_input": "3 5",
            "sample_output": "8",
            "test_cases": [
                {"input": "3 5", "output": "8", "is_sample": True, "points": 25},
                {"input": "0 0", "output": "0", "is_sample": False, "points": 25},
                {"input": "-5 10", "output": "5", "is_sample": False, "points": 25},
                {"input": "1000000000 1000000000", "output": "2000000000", "is_sample": False, "points": 25}
            ]
        },
        {
            "problem_id": "C",
            "title": "Even or Odd",
            "statement": """Given an integer N, determine if it is even or odd.

Input:
A single integer N (1 ≤ N ≤ 10^9)

Output:
Print "Even" if N is even, "Odd" if N is odd (without quotes)

Example 1:
Input: 4
Output: Even

Example 2:
Input: 7
Output: Odd""",
            "time_limit": 1.0,
            "memory_limit": 128,
            "difficulty": "easy",
            "points": 100,
            "sample_input": "4",
            "sample_output": "Even",
            "test_cases": [
                {"input": "4", "output": "Even", "is_sample": True, "points": 25},
                {"input": "7", "output": "Odd", "is_sample": False, "points": 25},
                {"input": "1", "output": "Odd", "is_sample": False, "points": 25},
                {"input": "1000000000", "output": "Even", "is_sample": False, "points": 25}
            ]
        },
        {
            "problem_id": "D",
            "title": "Factorial",
            "statement": """Calculate the factorial of N.

N! = 1 × 2 × 3 × ... × N
Note: 0! = 1 by definition

Input:
A single integer N (0 ≤ N ≤ 20)

Output:
N! (N factorial)

Example:
Input: 5
Output: 120

Explanation: 5! = 5 × 4 × 3 × 2 × 1 = 120""",
            "time_limit": 1.0,
            "memory_limit": 128,
            "difficulty": "medium",
            "points": 150,
            "sample_input": "5",
            "sample_output": "120",
            "test_cases": [
                {"input": "5", "output": "120", "is_sample": True, "points": 30},
                {"input": "0", "output": "1", "is_sample": False, "points": 30},
                {"input": "1", "output": "1", "is_sample": False, "points": 30},
                {"input": "10", "output": "3628800", "is_sample": False, "points": 30},
                {"input": "20", "output": "2432902008176640000", "is_sample": False, "points": 30}
            ]
        }
    ]

    for p in problems:
        # Insert problem
        c.execute("""
            INSERT OR REPLACE INTO problems 
            (problem_id, title, statement, time_limit, memory_limit, 
             difficulty, points, sample_input, sample_output, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (p["problem_id"], p["title"], p["statement"], p["time_limit"],
              p["memory_limit"], p["difficulty"], p["points"], 
              p["sample_input"], p["sample_output"], now))

        # Delete existing test cases
        c.execute("DELETE FROM test_cases WHERE problem_id = ?", (p["problem_id"],))

        # Insert test cases
        for tc in p["test_cases"]:
            output_hash = hash_output(tc["output"])
            sample_out = tc["output"] if tc["is_sample"] else ""
            c.execute("""
                INSERT INTO test_cases 
                (problem_id, input_data, output_hash, is_sample, sample_output, points)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (p["problem_id"], tc["input"], output_hash,
                  1 if tc["is_sample"] else 0, sample_out, tc.get("points", 0)))

    conn.commit()
    conn.close()
    print(f"✅ Added {len(problems)} sample problems!")


if __name__ == "__main__":
    print("=" * 50)
    print("  DCMS Database Setup")
    print("=" * 50)
    
    reset = input("\nReset database? (y/n): ").strip().lower() == 'y'
    setup_database(reset=reset)
    
    if input("Add sample problems? (y/n): ").strip().lower() == 'y':
        add_sample_problems()
    
    print("\n✅ Done!")