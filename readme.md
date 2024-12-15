# GenSearchGraph

This project leverages Google's Gemini AI model to generate Matplotlib graphs based on user-provided topics. It automates the process of searching for relevant information and creating a graph.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Introduction

This tool automates the creation of graphs by taking a user-defined topic as input. It uses Google's Gemini 2.0 model to first search for relevant information and then generates a Matplotlib graph based on the gathered data.

## Features

- **Automated Information Retrieval**: Uses Gemini's Google Search capabilities to gather data related to the user-provided topic.
- **AI-Powered Graph Generation**: Utilizes Google's Gemini AI to generate Python code for creating graphs.

## Installation

To get started with the Gemini Graph Generator, follow these steps:

1.  **Clone the repository**:

    ```sh
    git clone https://github.com/nassiramn/GenSearchGraph
    cd GenSearchGraph
    ```

2.  **Install the required dependencies**:

    ```sh
    pip install -r requirements.txt
    ```

3.  **Set up environment variables**:

    - Rename the .env.example file to .env
    - Add your Gemini API key to the `.env` file:

      ```
      GEMINI_API_KEY=your_api_key_here
      ```

      You can obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/).

## Usage

To run the Gemini Graph Generator, execute the following command:

```sh
python main.py
```

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Contact

For any inquiries or support, please contact me at git.nassir@gmail.com.
