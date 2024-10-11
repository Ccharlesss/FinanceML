# FinanceML
This project aims to build on fundamental aspects of web development, machine learning, probability and statistics, and finance to develop two robust models. The first model predicts the next day's closing price trend for stocks in the S&P 500, while the second model clusters the entire dataset based on annual average return and volatility, displaying the results on an interactive scatter plot. The goal is to assist users from diverse educational backgrounds in making more informed investment decisions.

Python was chosen for this project due to its extensive support for machine learning libraries. For the web framework, Python’s FastAPI was selected as a lightweight and widely-used option for developing machine learning web applications. On the client side, JavaScript with Material-UI was used to implement the components rendered to the user. Client-server communication is handled via HTTP protocols and Security is ensured using JWT token authentication and role-based access to critical administrative functions. 

The overall architecture follows the MVC (Model-View-Controller) design pattern. To facilitate deployment and manage system dependencies, Docker was used to containerize the application into microservices, each in its own environment. The application is divided into three containers: one for the backend, one for the frontend, and one for the database. The database container uses a PostgreSQL image pulled from Docker Hub to store the models' data.

The training dataset for the machine learning models is stored in a CSV file. To ensure the training data remains up to date, a scheduler was implemented using AWS Lambda to gather daily stock data from the S&P 500 and update the CSV file.


