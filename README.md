# Basic_Booking-Reservation_System-Backend-
A minimal backend service for booking resources like rooms or event slots using Flask. Includes user authentication, CRUD operations for resources, and booking functionality with validation to prevent double-booking. Expandable with additional features as needed.


#### API Usage Guide

This API provides routes for user registration, login, resource management, and bookings.

 **Header X-Token required** for all routes that require authentication.

1. **POST /register**
   - **Description:** Register a new user.
   - **Request body:** JSON or form data with the following fields:
     - `first_name`, `last_name`, `email`, `password`, `role`
   - **Response:** 
     - Success: `201` with user details (`id`, `email`).
     - Error: `400` with error message (e.g., missing fields).

2. **POST /login**
   - **Description:** Log in a user and obtain an access token.
   - **Request body:** JSON or form data with:
     - `email`, `password`
   - **Response:** 
     - Success: `200` with `token`.
     - Error: `401` with error message (e.g., invalid credentials).

3. **GET /resources**
   - **Description:** Get the list of resources (user only).
   - **Response:** 
     - Success: `200` with list of resources.
     - Error: `500` with error message.

4. **POST /resources**
   - **Description:** Create a new resource (admin only).
   - **Request body:** JSON or form data with:
     - `type`, `number`, `description`, `capacity`
   - **Response:** 
     - Success: `201` with resource `id`.
     - Error: `400` with missing fields error.

5. **POST /booking**
   - **Description:** Book a resource (user only).
   - **Request body:** JSON or form data with:
     - `resource`, `start_date`, `end_date`
   - **Response:** 
     - Success: `201` with booking status.
     - Error: `400` with missing fields error.

6. **GET /booking**
   - **Description:** List all bookings for the logged-in user.
   - **Response:** 
     - Success: `200` with list of bookings.
     - Error: `500` with error message.

---

#### Setting Up Locally

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/AfripulGroup/Basic_Booking-Reservation_System-Backend.git
   cd Basic_Booking-Reservation_System-Backend
   ```

2. **Install Dependencies:**
   - Ensure you have Python 3.9+ installed.
   - Create a virtual environment:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - Install required packages:
     ```bash
     pip install -r requirements.txt
     ```

3. **Set Up Environment Variables:**
   - Create a `.env` file in the root of the project and configure necessary environment variables (e.g., database URL, secret keys, etc.).
   - Example:
     ```
     DB_NAME=mongodb-db-name
     DB_ALIAS=mongodb-db-alias
     DB_HOST=redis-and-mongodb-host
     DB_PORT=mongodb-port
     ```

4. **Run the Flask App:**
   ```bash
   flask --app api.v1.app run
   ```
   OR
    
   ```bash
   export FLASK_APP=api.v1.app.run
   flask run
   ```
   
   - The application will be accessible at `http://127.0.0.1:5000`.

5. **Testing the API:**
   - You can test the API using tools like [Postman](https://www.postman.com/) or [cURL](https://curl.se/).
   - Ensure to pass the `X-Token` header for authentication where required.
