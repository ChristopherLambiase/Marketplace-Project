"""requesting.py — Database API endpoints for marketplace requests."""

import sqlite3
from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest
from db import get_db_connection

requests_bp = Blueprint('requesting', __name__)

@requests_bp.route('/send-request', methods=['POST'])
def send_request():
    """
    Send a Purchase Request
    ---
    tags:
      - Requests
    summary: Send a purchase request for an item
    description: Creates a new purchase request from a buyer to a seller for a specific item
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - item_id
            - buyer_id
            - message
          properties:
            item_id:
              type: integer
              example: 1
            buyer_id:
              type: integer
              example: 2
            message:
              type: string
              example: "I'm interested in this item. When can I pick it up?"
    responses:
      201:
        description: Request created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Request sent successfully"
            request_id:
              type: integer
              example: 5
            status:
              type: string
              example: "pending"
      400:
        description: Invalid input or missing fields
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Missing required fields"
      404:
        description: Item or user not found
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Item or buyer not found"
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

        # Required fields
        required_fields = ['item_id', 'buyer_id']
        missing_fields = [field for field in required_fields if not data.get(field)]

        if missing_fields:
            return jsonify({"message": f"Missing required fields: {missing_fields}"}), 400

        item_id = data['item_id']
        buyer_id = data['buyer_id']
        message = data.get('message', '')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify item and buyer both exist
        cursor.execute(
            """
            SELECT i.seller_id
            FROM items i
            WHERE i.id = ?
              AND EXISTS (SELECT 1 FROM users WHERE id = ?)
            """,
            (item_id, buyer_id)
        )
        item = cursor.fetchone()
        if not item:
            conn.close()
            return jsonify({"message": "Item or buyer not found"}), 404

        seller_id = item['seller_id']

        error_message = None

        if seller_id == buyer_id:
            error_message = "You cannot request your own item"
        else:
            # Check if a request already exists for this item by this buyer
            cursor.execute(
                'SELECT id FROM requests WHERE item_id = ? AND buyer_id = ? AND status != ?',
                (item_id, buyer_id, 'rejected')
            )
            if cursor.fetchone():
                error_message = "You already have a pending request for this item"

        if error_message:
            conn.close()
            return jsonify({"message": error_message}), 400

        # Create new request
        cursor.execute(
            '''INSERT INTO requests (item_id, buyer_id, seller_id, status, message)
               VALUES (?, ?, ?, ?, ?)''',
            (item_id, buyer_id, seller_id, 'pending', message)
        )

        request_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            "message": "Request sent successfully",
            "request_id": request_id,
            "status": "pending"
        }), 201

    except sqlite3.Error as error:
        return jsonify({"message": f"Database error: {str(error)}"}), 500
    except (KeyError, BadRequest) as error:
        return jsonify({"message": f"Invalid request data: {str(error)}"}), 400

@requests_bp.route('/get-approved-requests', methods=['GET'])
def get_approved_requests():
    """
    Get Approved Requests
    ---
    tags:
      - Requests
    summary: Retrieve approved requests
    description: Returns a list of all approved requests in the marketplace
    responses:
      200:
        description: Successfully retrieved approved requests
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              item:
                type: string
                example: "Laptop"
              requester:
                type: string
                example: "John Doe"
              status:
                type: string
                example: "approved"
              message:
                type: string
                example: "Interested in purchasing this item"
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
        conn = get_db_connection()

        sql = '''
        SELECT r.id, i.title as item, u.username as requester, r.status, r.message
        FROM requests r
        JOIN items i ON r.item_id = i.id
        JOIN users u ON r.buyer_id = u.id
        WHERE r.status = 'approved'
        ORDER BY r.updated_at DESC
        '''

        cursor = conn.execute(sql)
        requests_data = cursor.fetchall()

        result = []
        for req in requests_data:
            result.append({
                'id': req['id'],
                'item': req['item'],
                'requester': req['requester'],
                'status': req['status'],
                'message': req['message']
            })

        conn.close()
        return jsonify(result)

    except sqlite3.Error as db_error:
        return jsonify({'error': f'Database error: {str(db_error)}'}), 500
    except (TypeError, KeyError) as data_error:
        return jsonify({'error': f'Data error: {str(data_error)}'}), 500

@requests_bp.route('/get-incoming-requests', methods=['GET'])
def get_incoming_requests():
    """
    Get Incoming (Pending) Requests
    ---
    tags:
      - Requests
    summary: Retrieve incoming/pending requests
    description: Returns a list of all pending requests awaiting approval
    responses:
      200:
        description: Successfully retrieved incoming requests
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 3
              item:
                type: string
                example: "Monitor"
              requester:
                type: string
                example: "Alice Brown"
              status:
                type: string
                example: "pending"
              message:
                type: string
                example: "Would like to buy this monitor"
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
        conn = get_db_connection()

        sql = '''
        SELECT r.id, i.id as item_id, i.title as item, u.username as requester, r.status, r.message
        FROM requests r
        JOIN items i ON r.item_id = i.id
        JOIN users u ON r.buyer_id = u.id
        WHERE r.status = 'pending'
        ORDER BY r.created_at DESC
        '''

        cursor = conn.execute(sql)
        requests_data = cursor.fetchall()

        result = []
        for req in requests_data:
            result.append({
                'id': req['id'],
                'item_id': req['item_id'],
                'item': req['item'],
                'requester': req['requester'],
                'status': req['status'],
                'message': req['message']
            })

        conn.close()
        return jsonify(result)

    except sqlite3.Error as db_error:
        return jsonify({'error': f'Database error: {str(db_error)}'}), 500
    except (TypeError, KeyError) as data_error:
        return jsonify({'error': f'Data error: {str(data_error)}'}), 500

@requests_bp.route('/search-requests', methods=['GET'])
def search_requests():
    """
    Search Requests
    ---
    tags:
      - Requests
    summary: Search for requests
    description: Search for requests by item name or requester name, with optional status filtering
    parameters:
      - name: q
        in: query
        type: string
        required: false
        description: Search term (matches item or requester)
        example: "laptop"
      - name: status
        in: query
        type: string
        required: false
        description: Optional status filter
        enum: ["approved", "pending"]
        example: "approved"
    responses:
      200:
        description: Successfully retrieved filtered requests
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              item:
                type: string
                example: "Laptop"
              requester:
                type: string
                example: "John Doe"
              status:
                type: string
                example: "approved"
              message:
                type: string
                example: "Interested in this laptop"
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
        conn = get_db_connection()

        # Get query parameters
        search_query = request.args.get('q', '').lower()
        status_filter = request.args.get('status', None)

        # Build SQL query
        sql = '''
        SELECT r.id, i.title as item, u.username as requester, r.status, r.message
        FROM requests r
        JOIN items i ON r.item_id = i.id
        JOIN users u ON r.buyer_id = u.id
        WHERE 1=1
        '''
        params = []

        # Add search filter if provided
        if search_query:
            sql += ' AND (LOWER(i.title) LIKE ? OR LOWER(u.username) LIKE ?)'
            search_param = f'%{search_query}%'
            params.extend([search_param, search_param])

        # Add status filter if provided
        if status_filter:
            sql += ' AND r.status = ?'
            params.append(status_filter)

        sql += ' ORDER BY r.created_at DESC'

        cursor = conn.execute(sql, params)
        requests_data = cursor.fetchall()

        result = []
        for req in requests_data:
            result.append({
                'id': req['id'],
                'item': req['item'],
                'requester': req['requester'],
                'status': req['status'],
                'message': req['message']
            })

        conn.close()
        return jsonify(result)

    except sqlite3.Error as db_error:
        return jsonify({'error': f'Database error: {str(db_error)}'}), 500
    except (TypeError, KeyError) as data_error:
        return jsonify({'error': f'Data error: {str(data_error)}'}), 500

@requests_bp.route('/get-seller-requests/<int:seller_id>', methods=['GET'])
def get_seller_requests(seller_id):
    """
    Get Requests for Seller's Listings
    ---
    tags:
      - Requests
    summary: Retrieve requests for a specific seller's listings
    description: Returns a list of all requests for items posted by the specified seller
    parameters:
      - name: seller_id
        in: path
        type: integer
        required: true
        description: ID of the seller
        example: 1
    responses:
      200:
        description: Successfully retrieved seller's requests
        schema:
          type: object
          properties:
            requests:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  item_id:
                    type: integer
                    example: 1
                  item_title:
                    type: string
                    example: "Laptop"
                  requester:
                    type: string
                    example: "John Doe"
                  status:
                    type: string
                    example: "pending"
                  message:
                    type: string
                    example: "Interested in this laptop"
                  created_at:
                    type: string
                    example: "2025-11-03 20:51:16"
            total_count:
              type: integer
              example: 2
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
        conn = get_db_connection()

        sql = '''
        SELECT r.id, r.item_id, i.title as item_title, u.username as requester, 
               r.status, r.message, r.created_at
        FROM requests r
        JOIN items i ON r.item_id = i.id
        JOIN users u ON r.buyer_id = u.id
        WHERE r.seller_id = ?
        ORDER BY r.created_at DESC
        '''

        cursor = conn.execute(sql, [seller_id])
        requests_data = cursor.fetchall()

        result = []
        for req in requests_data:
            result.append({
                'id': req['id'],
                'item_id': req['item_id'],
                'item_title': req['item_title'],
                'requester': req['requester'],
                'status': req['status'],
                'message': req['message'],
                'created_at': req['created_at']
            })

        conn.close()
        return jsonify({
            'requests': result,
            'total_count': len(result)
        })

    except sqlite3.Error as db_error:
        return jsonify({'error': f'Database error: {str(db_error)}'}), 500
    except (TypeError, KeyError) as data_error:
        return jsonify({'error': f'Data error: {str(data_error)}'}), 500

@requests_bp.route('/get-buyer-requests/<int:buyer_id>', methods=['GET'])
def get_buyer_requests(buyer_id):
    """
    Get Requests Made by a Specific Buyer
    ---
    tags:
      - Requests
    summary: Retrieve requests made by a specific buyer
    description: Returns all requests (pending, approved, rejected) made by the specified buyer
    parameters:
      - name: buyer_id
        in: path
        type: integer
        required: true
        description: ID of the buyer
        example: 2
      - name: status
        in: query
        type: string
        required: false
        description: Optional status filter
        enum: ["approved", "pending", "rejected"]
        example: "approved"
    responses:
      200:
        description: Successfully retrieved buyer's requests
        schema:
          type: object
          properties:
            requests:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  item_id:
                    type: integer
                    example: 1
                  item_title:
                    type: string
                    example: "Laptop"
                  seller:
                    type: string
                    example: "John Doe"
                  status:
                    type: string
                    example: "approved"
                  message:
                    type: string
                    example: "Interested in this laptop"
                  created_at:
                    type: string
                    example: "2025-11-03 20:51:16"
            total_count:
              type: integer
              example: 2
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
        conn = get_db_connection()
        status_filter = request.args.get('status', None)

        sql = '''
        SELECT r.id, r.item_id, i.title as item_title, u.username as seller, 
               r.status, r.message, r.created_at
        FROM requests r
        JOIN items i ON r.item_id = i.id
        JOIN users u ON i.seller_id = u.id
        WHERE r.buyer_id = ?
        '''
        params = [buyer_id]

        if status_filter:
            sql += ' AND r.status = ?'
            params.append(status_filter)

        sql += ' ORDER BY r.created_at DESC'

        cursor = conn.execute(sql, params)
        requests_data = cursor.fetchall()

        result = []
        for req in requests_data:
            result.append({
                'id': req['id'],
                'item_id': req['item_id'],
                'item_title': req['item_title'],
                'seller': req['seller'],
                'status': req['status'],
                'message': req['message'],
                'created_at': req['created_at']
            })

        conn.close()
        return jsonify({
            'requests': result,
            'total_count': len(result)
        })

    except sqlite3.Error as db_error:
        return jsonify({'error': f'Database error: {str(db_error)}'}), 500
    except (TypeError, KeyError) as data_error:
        return jsonify({'error': f'Data error: {str(data_error)}'}), 500

@requests_bp.route('/update-request-status/<int:request_id>', methods=['POST'])
def update_request_status(request_id):
    """
    Update Request Status
    ---
    tags:
      - Requests
    summary: Update the status of a request (approve or deny)
    description: Allows a seller to approve or reject a purchase request for their item
    parameters:
      - name: request_id
        in: path
        type: integer
        required: true
        description: ID of the request to update
        example: 1
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - status
            - seller_id
          properties:
            status:
              type: string
              enum: ["approved", "rejected"]
              example: "approved"
            seller_id:
              type: integer
              description: ID of the seller (for authorization)
              example: 1
    responses:
      200:
        description: Request status updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Request status updated successfully"
            request_id:
              type: integer
              example: 1
            status:
              type: string
              example: "approved"
      400:
        description: Invalid status or missing fields
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Invalid status. Must be 'approved' or 'rejected'"
      403:
        description: Unauthorized - seller does not own the item
        schema:
          type: object
          properties:
            message:
              type: string
              example: "You are not authorized to update this request"
      404:
        description: Request not found
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Request not found"
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

        status = data.get('status', '').lower()
        seller_id = data.get('seller_id')

        # Validate status value
        if status not in ['approved', 'rejected'] or not status or not seller_id:
            return jsonify({"message": "Invalid/Missing fields."}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify request exists and get seller_id from the request
        cursor.execute('SELECT seller_id FROM requests WHERE id = ?', (request_id,))
        req = cursor.fetchone()
        if not req:
            conn.close()
            return jsonify({"message": "Request not found"}), 404

        # Verify the seller owns this request (authorization check)
        if req['seller_id'] != seller_id:
            conn.close()
            return jsonify({"message": "You are not authorized to update this request"}), 403

        # Update request status
        cursor.execute(
            'UPDATE requests SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (status, request_id)
        )

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Request status updated successfully",
            "request_id": request_id,
            "status": status
        }), 200

    except sqlite3.Error as error:
        return jsonify({"message": f"Database error: {str(error)}"}), 500
    except (KeyError, BadRequest) as error:
        return jsonify({"message": f"Invalid request data: {str(error)}"}), 400
