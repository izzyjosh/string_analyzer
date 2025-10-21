# String Analyzer Service 

A Fastapi application that stores strings and some of its properties. The project analyzes the given string amd stores it togetger with its properties.

# Features

- Tell of the word or phrase is palindromic
- Gives the length of the word or phrase
- The number of words present
- Handles getting of words properties with query filters
- Handles natural language filtering
- It tells the number of unique character present as well as their frequencies


## 🧰 Tech Stack

- **Python 3.12+**
- **FastAPI** — for the web framework
- **Uvicorn** — for running the ASGI serve

 
 ## 📦 Setup Instructions

 Follow these steps to set up and run the project locally.

 ### 1. Clone the Repository
 ```bash
 git clone https://github.com/izzyjosh/string_analyzer.git
 cd string_analyzer
 ```

 ### 2. Create a virtual environment
 ```
 python -m venv .venv
 source .venv/bin/activate
 ```

 ### 3. Install dependencies
 ```
 pip install -r requirements.txt
```
### 4. Finally, run the project using
 ```
python main.py
```
