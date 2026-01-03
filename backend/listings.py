"""listings.py — Database API endpoints for marketplace listings"""

import json
import sqlite3
from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest
from db import get_db_connection


listings_bp = Blueprint('listings_api', __name__)

@listings_bp.route('/get-all-listings', methods=['GET'])
def get_all_listings():
    """
    Get All Listings
    ---
    tags:
      - Listings
    summary: Retrieve all available listings
    description: Returns a list of all available listings in the marketplace
    responses:
      200:
        description: List of all available listings in the marketplace
        schema:
          type: object
          properties:
            listings:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  title:
                    type: string
                    example: "MacBook Pro 13-inch"
                  description:
                    type: string
                    example: "Gently used MacBook Pro, perfect for students"
                  price:
                    type: number
                    example: 800.00
                  category:
                    type: string
                    example: "Electronics"
                  condition:
                    type: string
                    example: "Good"
                  seller_name:
                    type: string
                    example: "John Doe"
                  location:
                    type: string
                    example: "Campus Library"
                  status:
                    type: string
                    example: "available"
            total_count:
              type: integer
              example: 4
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = '''
        SELECT i.id, i.title, i.description, i.price, i.category, i.condition,
               i.seller_id, u.username as seller_name, i.location, i.status, 
               i.images, i.date_posted
        FROM items i
        JOIN users u ON i.seller_id = u.id
        WHERE i.status = 'available'
        ORDER BY i.date_posted DESC
        '''
        cursor.execute(sql)
        items = cursor.fetchall()
        listings = []
        for item in items:
            listing = {
                'id': item['id'],
                'title': item['title'],
                'description': item['description'],
                'price': float(item['price']),
                'category': item['category'],
                'condition': item['condition'],
                'seller_id': item['seller_id'],
                'seller_name': item['seller_name'],
                'location': item['location'],
                'status': item['status'],
                'date_posted': item['date_posted'],
                'images': json.loads(item['images']) if item['images'] else []
            }
            listings.append(listing)
        conn.close()
        return jsonify({
            "listings": listings,
            "total_count": len(listings)
        })
    except sqlite3.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except (TypeError, KeyError) as data_error:
        return jsonify({"error": f"Data error: {str(data_error)}"}), 500

@listings_bp.route('/post-listing', methods=['POST'])
def post_listing():
    """
    Post New Listing
    ---
    tags:
      - Listings
    summary: Create a new listing
    description: Creates a new marketplace listing with the provided information
    parameters:
      - name: listing_data
        in: body
        required: true
        schema:
          type: object
          required:
            - title
            - description
            - price
            - category
            - condition
            - seller_id
            - location
          properties:
            title:
              type: string
              example: "iPhone 12"
            description:
              type: string
              example: "Barely used iPhone 12 in excellent condition"
            price:
              type: number
              example: 500.00
            category:
              type: string
              example: "Electronics"
            condition:
              type: string
              example: "Excellent"
            seller_id:
              type: integer
              example: 1
            location:
              type: string
              example: "Student Center"
            images:
              type: array
              items:
                type: string
              example: ["image1.jpg", "image2.jpg"]
    responses:
      201:
        description: Listing created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Listing created successfully"
            listing:
              type: object
              properties:
                id:
                  type: integer
                  example: 5
                title:
                  type: string
                  example: "iPhone 12"
                price:
                  type: number
                  example: 500.00
      400:
        description: Missing required fields
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Missing required fields: ['title']"
      500:
        description: Database error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Database error: connection failed"
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validate required fields
        required_fields = ['title', 'description', 'price', 'category',
                           'condition', 'seller_id', 'location']

        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {missing_fields}"}), 400

        # Verify seller exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE id = ?', (data['seller_id'],))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": f"Seller {data['seller_id']} not found"}), 404

        # Convert images list to JSON string
        images_json = json.dumps(data.get("images", []))

        # Insert new listing
        cursor.execute(
            '''INSERT INTO items
               (title, description, price, category, condition, seller_id,
                location, images, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (data['title'], data['description'], float(data['price']),
             data['category'], data['condition'], data['seller_id'],
             data['location'], images_json, 'available')
        )

        listing_id = cursor.lastrowid
        conn.commit()

        # Fetch the newly created listing with seller info
        cursor.execute(
            '''SELECT i.id, i.title, i.description, i.price, i.category, i.condition,
                      i.seller_id, u.username as seller_name, i.location, i.status,
                      i.images, i.date_posted
               FROM items i
               JOIN users u ON i.seller_id = u.id
               WHERE i.id = ?''',
            (listing_id,)
        )
        item = cursor.fetchone()
        conn.close()

        listing = {
            'id': item['id'],
            'title': item['title'],
            'description': item['description'],
            'price': float(item['price']),
            'category': item['category'],
            'condition': item['condition'],
            'seller_id': item['seller_id'],
            'seller_name': item['seller_name'],
            'location': item['location'],
            'status': item['status'],
            'date_posted': item['date_posted'],
            'images': json.loads(item['images']) if item['images'] else []
        }

        return jsonify({
            "message": "Listing created successfully",
            "listing": listing
        }), 201

    except sqlite3.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except (KeyError, BadRequest, ValueError) as error:
        return jsonify({"error": f"Invalid request data: {str(error)}"}), 400

@listings_bp.route('/get-my-listings', methods=['GET'])
def get_my_listings():
    """
    Get Current User's Listings
    ---
    tags:
      - Listings
    summary: Get listings for a specific user
    description: Returns all listings posted by the specified user
    parameters:
      - name: user_id
        in: query
        type: integer
        required: true
        description: ID of the current user
        example: 1
    responses:
      200:
        description: List of listings posted by the current user
        schema:
          type: object
          properties:
            user_listings:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  title:
                    type: string
                    example: "MacBook Pro 13-inch"
                  price:
                    type: number
                    example: 800.00
                  status:
                    type: string
                    example: "available"
                  date_posted:
                    type: string
                    example: "2024-10-15"
            total_count:
              type: integer
              example: 2
            user_id:
              type: integer
              example: 1
      400:
        description: Missing user_id parameter
        schema:
          type: object
          properties:
            error:
              type: string
              example: "user_id parameter is required"
      500:
        description: Database error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Database error: connection failed"
    """
    try:
        user_id = request.args.get('user_id', type=int)

        if not user_id:
            return jsonify({"error": "user_id parameter is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''SELECT id, title, description, price, category, condition,
                      seller_id, location, status, images, date_posted
               FROM items
               WHERE seller_id = ?
               ORDER BY date_posted DESC''',
            (user_id,)
        )
        items = cursor.fetchall()

        user_listings = []
        for item in items:
            listing = {
                'id': item['id'],
                'title': item['title'],
                'description': item['description'],
                'price': float(item['price']),
                'category': item['category'],
                'condition': item['condition'],
                'location': item['location'],
                'status': item['status'],
                'date_posted': item['date_posted'],
                'images': json.loads(item['images']) if item['images'] else []
            }
            user_listings.append(listing)

        conn.close()
        return jsonify({
            "user_listings": user_listings,
            "total_count": len(user_listings),
            "user_id": user_id
        })

    except sqlite3.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except (TypeError, KeyError) as data_error:
        return jsonify({"error": f"Data error: {str(data_error)}"}), 500

@listings_bp.route('/get-item-listing', methods=['GET'])
def get_item_listing():
    """
    Get Item Listing by ID
    ---
    tags:
      - Listings
    summary: Get specific item listing
    description: Returns a specific item listing by ID
    parameters:
      - name: item_id
        in: query
        type: integer
        required: true
        description: ID of the item
        example: 1
    responses:
      200:
        description: Returns item listing
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            title:
              type: string
              example: "Laptop"
            seller_name:
              type: string
              example: "John Doe"
            description:
              type: string
              example: "Acer 15 inch laptop"
            price:
              type: number
              example: 1000.0
            images:
              type: array
              items:
                type: string
            category:
              type: string
              example: "Electronics"
            condition:
              type: string
              example: "Good"
            location:
              type: string
              example: "Campus Library"
            status:
              type: string
              example: "available"
      404:
        description: Item not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Item not found"
      500:
        description: Database error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Database error: connection failed"
    """
    try:
        item_id = request.args.get('item_id', type=int)

        if not item_id:
            return jsonify({"error": "item_id parameter is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''SELECT i.id, i.title, i.description, i.price, i.category, i.condition,
                      i.seller_id, u.username as seller_name, i.location, i.status,
                      i.images, i.date_posted
               FROM items i
               JOIN users u ON i.seller_id = u.id
               WHERE i.id = ?''',
            (item_id,)
        )
        item = cursor.fetchone()
        conn.close()

        if not item:
            return jsonify({"error": "Item not found"}), 404

        listing = {
            'id': item['id'],
            'title': item['title'],
            'description': item['description'],
            'price': float(item['price']),
            'category': item['category'],
            'condition': item['condition'],
            'seller_id': item['seller_id'],
            'seller_name': item['seller_name'],
            'location': item['location'],
            'status': item['status'],
            'date_posted': item['date_posted'],
            'images': json.loads(item['images']) if item['images'] else []
        }

        return jsonify(listing)

    except sqlite3.Error as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
    except (TypeError, KeyError) as data_error:
        return jsonify({"error": f"Data error: {str(data_error)}"}), 500
