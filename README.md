# crowScrape

## Overview
`crowScrape` is a simple, yet powerful, web scraper designed to collect prices on computer hardware. It is written in Django, a high-level Python Web framework that encourages rapid development and clean, pragmatic design.

## Use Case
This tool is perfect for anyone looking to keep track of computer hardware prices. Whether you're a gamer looking for the best deals on the latest graphics cards, or a business owner trying to minimize costs, `crowScrape` can help you stay informed and make better purchasing decisions.

## Tech Stack
- **Django**: A high-level Python Web framework that encourages rapid development and clean, pragmatic design.
- **Python**: A popular programming language known for its simplicity and readability.
- **BeautifulSoup**: A Python library for pulling data out of HTML and XML files.
- **Redis**: Commonly used for in-memory data caching, primarily used for storing ephemeral key:value pairs.
- **PostgeSQL**: Popular SQL Database used for storing all data related to the scraper and user data.

## Setup
1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the required dependencies with `pip install -r requirements.txt`.
4. Run `python manage.py migrate`
6. Run the Django server with `python manage.py runserver`.
7. Open your web browser and navigate to `localhost:8000` to start using `crowScrape`.

## Contributing
We welcome contributions from the community. If you'd like to contribute, please fork the repository, make your changes, and submit a pull request. We'll review it as soon as we can.

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.
