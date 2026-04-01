# 🗄️ Building a Simple Database in Python

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Database internals](https://img.shields.io/badge/Database-Internals-blue?style=for-the-badge)

A from-scratch implementation of a SQLite-like database relational engine written entirely in Python. 

This project is a Pythonic adaptation of the famous [Let's Build a Simple Database](https://cstack.github.io/db_tutorial/) C tutorial by cstack. It explores how to translate low-level manual memory management (`malloc`, pointers, raw byte arrays) into a high-level, object-oriented language using Python's `struct` and `bytearray` capabilities, without sacrificing the core architectural concepts of a real database.

## 📖 Companion Article Series

I documented the entire process of building this engine step-by-step. If you are curious about database internals, check out the series:

[Read Article](https://www.notion.so/creedthoughts/Python-SQLite-Clone-331422ab558c802fb3c6c379f2e5f280) 

| Part | Topic | Description | Link |
| :--- | :--- | :--- | :--- |
| **Part 1** | **Getting Started** | Building the REPL heartbeat and the front-end compiler to parse Meta-commands vs. SQL statements. | [Read Article]([https://www.notion.so/creedthoughts/Getting-Started-335422ab558c80dd90eee21a656ec650]) |
| **Part 2** | **Basic Table** | Moving from dynamic strings to rigid memory. Using `struct` to pack rows into fixed-size byte arrays. | [Read Article]([https://www.notion.so/creedthoughts/Basic-Table-331422ab558c80c4a158fc188005c3e3]) |
| **Part 3** | **Tests & Validation** | Building an automated integration suite and enforcing strict column-size limits to prevent memory corruption. | [Read Article]([https://www.notion.so/creedthoughts/Tests-Validation-331422ab558c80e39eecc662c3a40da1]) |
| **Part 4** | **Persistence** | Building the `Pager` to save data to disk, caching 4KB pages in memory to mirror OS-level paging. | [Read Article]([https://www.notion.so/creedthoughts/Persistance-331422ab558c803eb8c4d81f9b028e3d]) |
| **Part 5** | **Adding a Cursor** | Decoupling execution logic from the storage array using abstract pointers to prepare for tree structures. | [Read Article]([https://www.notion.so/creedthoughts/Adding-a-Cursor-332422ab558c802487dbd92f6f8a4b70]) |

*(More coming soon as we dive into B-Trees!)*

## ✨ Current Features

* **Interactive REPL:** A read-execute-print loop that acts as the primary interface.
* **Front-end Compiler:** Validates syntax, enforces strict column byte-limits, and prevents negative IDs.
* **Binary Serialization:** Uses Python's `struct` module to pack data into raw bytes, simulating C's memory layout.
* **Disk Persistence:** A `Pager` class that reads/writes data to a `.db` file in 4KB chunks.
* **Cursor Navigation:** Abstracted pointers that track `page_num` and `cell_num` for traversing the database layout.
* **Test Isolation:** An automated test suite using `unittest` and `subprocess` to ensure data integrity across sessions.

## 🚀 Quick Start

**Requirements:** Python 3.x (No external dependencies!)

**1. Start the Database**
Provide a filename to start the REPL. If the file doesn't exist, it will be created.
```bash
python db.py mydb.db
2. Insert and Retrieve DataPlaintextdb > insert 1 alice alice@example.com
Executed.
db > insert 2 bob bob@example.com
Executed.
db > select
(1, alice, alice@example.com)
(2, bob, bob@example.com)
Executed.
db > .exit
```

(Your data is now safely saved to mydb.db! Run the program again to see it persist.)

### 🧪 Running the Tests
The project includes an integration test suite that spins up the REPL in a subprocess, feeds it commands, and verifies the output.
``` Bash
python test_db.py
```

### 🏗️ What's Next?
The current implementation uses a flat B-Tree Node structure (a single root leaf node). The next major architectural shift is implementing B-Tree Node Splitting to support internal nodes and efficient $O(\log n)$ lookups!