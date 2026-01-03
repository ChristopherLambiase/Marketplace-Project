"""user.py — API endpoints for user with database integration"""

import hashlib
import sqlite3
from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest
from db import get_db_connection

user_bp = Blueprint('user_api', __name__)

def hash_password(password):
    """Hash a password for storing"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

@user_bp.route('/register', methods=['POST'])
def register():
    """
    User Registration
    ---
    tags:
      - User
    summary: Register a new user
    description: Creates a new user account
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              example: "john_doe"
            email:
              type: string
              example: "john@example.com"
            password:
              type: string
              example: "securepassword"
    responses:
      201:
        description: User created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "User registered successfully"
            user_id:
              type: integer
              example: 5
      400:
        description: Invalid input or user already exists
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Missing required fields"
      500:
        description: Database error
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Database error: connection failed"
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"message": "No data provided"}), 400

        # Required fields
        required_fields = ['username', 'email', 'password']
        missing_fields = [field for field in required_fields if not data.get(field)]

        if missing_fields:
            return jsonify({"message": f"Missing required fields: {missing_fields}"}), 400

        username = data['username']
        email = data['email']
        password = data['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
        if cursor.fetchone():
            conn.close()
            return jsonify({"message": "Username or email already exists"}), 400

        # Create new user
        cursor.execute(
            '''INSERT INTO users (username, email, password_hash)
               VALUES (?, ?, ?)''',
            (username, email, hash_password(password))
        )

        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            "message": "User registered successfully",
            "user_id": user_id
        }), 201

    except sqlite3.Error as error:
        return jsonify({"message": f"Database error: {str(error)}"}), 500
    except (KeyError, BadRequest) as error:
        return jsonify({"message": f"Invalid request data: {str(error)}"}), 400

@user_bp.route('/login', methods=['POST'])
def login():
    """
    User Login
    ---
    tags:
      - User
    summary: Authenticate user login
    description: Authenticates user credentials and returns a token
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "john_doe"
            password:
              type: string
              example: "securepassword"
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Login successful"
            token:
              type: string
              example: "mock-jwt-token-1"
            user_id:
              type: integer
              example: 1
            user_info:
              type: object
              properties:
                username:
                  type: string
                  example: "john_doe"
                email:
                  type: string
                  example: "john@example.com"

      400:
        description: Missing required fields
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Missing required fields"
      401:
        description: Invalid credentials
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Invalid username or password"
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"message": "No data provided"}), 400

        username = data.get('username')
        password = data.get('password')

        if not all([username, password]):
            return jsonify({"message": "Missing required fields"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT id, username, email
               FROM users WHERE username = ? AND password_hash = ?''',
            (username, hash_password(password))
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            return jsonify({
                "message": "Login successful",
                "token": f"mock-jwt-token-{user['id']}",
                "user_id": user['id'],
                "user_info": {
                    "username": user['username'],
                    "email": user['email'],
                }
            }), 200

        return jsonify({"message": "Invalid username or password"}), 401

    except sqlite3.Error as error:
        return jsonify({"message": f"Database error: {str(error)}"}), 500
    except (KeyError, BadRequest) as error:
        return jsonify({"message": f"Invalid request data: {str(error)}"}), 400

@user_bp.route('/get-user-profile/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    """
    Get User Profile
    ---
    tags:
      - User
    summary: Retrieve user profile
    description: Returns the user's profile information
    parameters:
      - name: user_id
        in: path
        required: true
        type: integer
        description: ID of the user
        example: 1
    responses:
      200:
        description: Successfully retrieved user profile
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            username:
              type: string
              example: "john_doe"
            email:
              type: string
              example: "john@example.com"
            created_at:
              type: string
              example: "2024-10-15 10:30:00"
      404:
        description: User not found
        schema:
          type: object
          properties:
            message:
              type: string
              example: "User not found"
      500:
        description: Database error
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Database error: connection failed"
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT id, username, email, created_at
               FROM users WHERE id = ?''',
            (user_id,)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            return jsonify({
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "created_at": user['created_at']
            }), 200

        return jsonify({"message": "User not found"}), 404

    except sqlite3.Error as error:
        return jsonify({"message": f"Database error: {str(error)}"}), 500
    except (KeyError, ValueError) as error:
        return jsonify({"message": f"Invalid data format: {str(error)}"}), 400

@user_bp.route('/update-user-profile', methods=['POST'])
def update_user_profile():
    """
    Update User Profile
    ---
    tags:
      - User
    summary: Update user profile information
    description: Updates the user's profile with provided information
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - user_id
          properties:
            user_id:
              type: integer
              example: 1
            email:
              type: string
              example: "newemail@example.com"
    responses:
      200:
        description: Profile updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Profile updated successfully"
      400:
        description: Missing required fields or validation error
        schema:
          type: object
          properties:
            message:
              type: string
              example: "user_id is required"
      404:
        description: User not found
        schema:
          type: object
          properties:
            message:
              type: string
              example: "User not found"
      500:
        description: Database error
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Database error: connection failed"
    """
    try:
        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({"message": "user_id is required"}), 400

        user_id = data['user_id']
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"message": "User not found"}), 404

        # Build update query dynamically
        update_fields = []
        update_values = []
        result = {"status": "error", "code": 400, "message": ""}

        updatable_fields = ['email']
        for field in updatable_fields:
            if field in data and data[field] is not None:
                update_fields.append(f"{field} = ?")
                update_values.append(data[field])

        if not update_fields:
            result = {"status": "error", "code": 400, "message": "No valid fields to update"}
        else:
            # Check email uniqueness if being updated
            if 'email' in data:
                cursor.execute(
                    'SELECT id FROM users WHERE email = ? AND id != ?',
                    (data['email'], user_id)
                )
                if cursor.fetchone():
                    result = {"status": "error", "code": 400, "message": "Email already exists"}
                else:
                    # Perform update
                    update_values.append(user_id)
                    sql = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
                    cursor.execute(sql, update_values)
                    conn.commit()
                    result = {
                        "status": "success",
                        "code": 200,
                        "message": "Profile updated successfully"
                    }

        conn.close()
        return jsonify({"message": result["message"]}), result["code"]

    except sqlite3.Error as error:
        return jsonify({"message": f"Database error: {str(error)}"}), 500
    except (KeyError, ValueError) as error:
        return jsonify({"message": f"Invalid data format: {str(error)}"}), 400

@user_bp.route('/users', methods=['GET'])
def get_all_users():
    """
    Get All Users
    ---
    tags:
      - User
    summary: Retrieve all users
    description: Returns a list of all users (id and username)
    responses:
      200:
        description: List of users
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              name:
                type: string
                example: "john_doe"
      500:
        description: Database error
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Database error: connection failed"
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username FROM users')
        users = cursor.fetchall()
        conn.close()
        # Convert to list of dicts
        user_list = [{"id": user["id"], "name": user["username"]} for user in users]
        return jsonify(user_list), 200
    except sqlite3.Error as error:
        return jsonify({"message": f"Database error: {str(error)}"}), 500
