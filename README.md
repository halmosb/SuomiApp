# Python Language Learning App

Welcome to my **Language Learning App**! This is a versatile and user-friendly tool designed to help you master a new language effectively. The main puropse of the app is to help practice vocabulary.

## Running Suomiapp on Windows

Follow these instructions to set up the local environment and run the application without syncing thousands of virtual environment files to OneDrive.

### Prerequisites: Install uv

Open **PowerShell** and run the official standalone installer:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

*Note: After the installation completes, close your current terminal window and open a new one to refresh your system PATH variables.*

### Step 1: Redirect the Virtual Environment Path

Set the environment variable to force `uv` to build and read your virtual environment from your local hard drive instead of the shared OneDrive directory:

```powershell
$env:UV_PROJECT_ENVIRONMENT = "C:\Users\$env:USERNAME\.virtualenvs\suomiapp"
```

### Step 2: Install Dependencies and Run the App

1. Sync your project dependencies. This command automatically initializes and updates the virtual environment at the isolated local path you configured above:
   ```powershell
   uv sync
   ```

2. Execute your application script through `uv`:
   ```powershell
   uv run main.py
   ```

## Features

### 1. Flashcards
- **Interactive learning**: Quickly learn and review vocabulary with flashcards.
- **Spaced repetition**: Enhance retention by reviewing terms at optimal intervals.

### 2. Write Mode
- **Dynamic settings**: Tailor your practice sessions to your needs with options.
- **Real-time feedback**: Receive instant corrections.

### 3. Automatic Translation
- **Multilingual support**: Translate terms or phrases into multiple languages.

### 4. Text-to-Speech (Reading Terms)
- **Pronunciation practice**: Listen to native pronunciations for every term.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/halmosb/SuomiApp.git
   ```
2. Navigate to the project directory:
   ```bash
   cd python-language-learning-app
   ```
3. Run the application:
   ```bash
   python app.py
   ```

## Usage

1. Launch the app and select the feature you want to use, the word lists are read from a file, then you can practice:
   - **Flashcards**: Flashcards are a good way to start with unknown vocabulary.
   - **Write Mode**: Configure settings and start your writing exercises.
   - **Automatic Translation**: Input the term or phrase for instant translation.
   - **Text-to-Speech**: Listen to accurate pronunciations for better language immersion.

2. Follow the prompts to complete your learning tasks.

## Contributing

Contributions are welcome! If you have ideas for new features, bug fixes, or improvements, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or fix:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature or fix description"
   ```
4. Push to your fork:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request on the main repository.

## Acknowledgments

Thank you for using the Python Language Learning App. Your feedback and support make this project better every day!

