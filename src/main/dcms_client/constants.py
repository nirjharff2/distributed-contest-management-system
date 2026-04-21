"""Client theme, languages, and server URL."""
import sys

SERVER_WS = "ws://127.0.0.1:8000/ws"

COLORS = {
    "bg_dark": "#0d1117",
    "bg_medium": "#161b22",
    "bg_light": "#21262d",
    "bg_editor": "#1e2228",
    "accent": "#58a6ff",
    "success": "#3fb950",
    "error": "#f85149",
    "warning": "#d29922",
    "text": "#c9d1d9",
    "text_secondary": "#8b949e",
    "keyword": "#ff7b72",
    "string": "#a5d6ff",
    "comment": "#8b949e",
    "number": "#79c0ff",
    "high_priority": "#f85149",
    "normal_priority": "#d29922",
    "low_priority": "#8b949e",
}

LANGUAGES = {
    "Python": {
        "id": "python",
        "extension": ".py",
        "compile": None,
        "run": [sys.executable, "{file}"],
        "template": '# Python Solution\n\n# Read input\n# n = int(input())\n# a, b = map(int, input().split())\n# nums = list(map(int, input().split()))\n\n# Your code here\nprint("Hello, World!")\n'
    },
    "C++": {
        "id": "cpp",
        "extension": ".cpp",
        "compile": ["g++", "-O2", "-std=c++17", "-o", "{output}", "{file}"],
        "run": ["{output}"],
        "template": '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios_base::sync_with_stdio(false);\n    cin.tie(NULL);\n    \n    // Your code here\n    cout << "Hello, World!" << endl;\n    \n    return 0;\n}\n'
    },
    "Java": {
        "id": "java",
        "extension": ".java",
        "compile": ["javac", "{file}"],
        "run": ["java", "-cp", "{dir}", "Main"],
        "template": 'import java.util.*;\nimport java.io.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        \n        // Your code here\n        System.out.println("Hello, World!");\n    }\n}\n'
    },
    "C": {
        "id": "c",
        "extension": ".c",
        "compile": ["gcc", "-O2", "-o", "{output}", "{file}"],
        "run": ["{output}"],
        "template": '#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n\nint main() {\n    // Your code here\n    printf("Hello, World!\\n");\n    return 0;\n}\n'
    }
}
