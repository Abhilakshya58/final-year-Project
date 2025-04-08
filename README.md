### 1. **Cloning the Repository**

First, each team member should clone the repository to their local machine:

```bash
git clone https://github.com/Abhilakshya58/final-year-Project.git
```

### 2. **Setting Up the Environment**

Since the project contains Python files and a `setup.py`, it's advisable to use a virtual environment to manage dependencies.

#### a. Navigate to the Project Directory

```bash
cd final-year-Project
```
#### b.  Create a Virtual Environment
```bash
python -m venv .venv
```

#### c.  Activate the Virtual Environment
```bash
.venv\Scripts\activate
```
### 3. **3. Install Dependencies**
```bash
pip install -e .
```

### 4. **Make the CLI Executable**
```bash
chmod +x ugit
```
### 5. **Commadns that ran so far**

 ### a. Initialize a Repository:
 ```bash
./ugit init
```

 ### b. Commit Changes:
 ```bash
./ugit commit -m "Initial commit"
```

 ### c. Tag a Commit:
 ```bash
./ugit tag v1.0
```

 ### d. View Commit History:
 ```bash
./ugit log
```

 ### e. Visualize Commit Graph:
 ```bash
./ugit k

```
