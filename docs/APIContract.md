## file requesting.py

1. **get-approved-requests**
   - **HTTP Method & Route**: GET /get-approved-requests
   - **Input**: None
   - **Output**: application/json
   ```json
   [
     {
       "id": 1,
       "item": "Laptop",
       "requester": "John Doe",
       "status": "approved"
     },
     {
       "id": 2,
       "item": "Desk Chair",
       "requester": "Jane Smith",
       "status": "approved"
     }
   ]
   ```

2. **get-incoming-requests**
   - **HTTP Method & Route**: GET /get-incoming-requests
   - **Input**: None
   - **Output**: application/json
   ```json
   [
     {
       "id": 3,
       "item": "Monitor",
       "requester": "Alice Brown",
       "status": "pending"
     },
     {
       "id": 4,
       "item": "Keyboard",
       "requester": "David Green",
       "status": "pending"
     }
   ]
   ```

3. **search-requests**
   - **HTTP Method & Route**: GET /search-requests
   - **Input**: 
     - Query Parameters:
       - `q` (string, required): Search term to filter requests
       - `status` (string, optional): Filter by status ("approved" or "pending")
   - **Output**: application/json
   ```json
   [
     {
       "id": 1,
       "item": "Laptop",
       "requester": "John Doe",
       "status": "approved"
     }
   ]
   ```

## file user.py

4. **login**
   - **HTTP Method & Route**: POST /login
   - **Input**: application/json
   ```json
   {
     "username": "nickiminaj",
     "password": "password123"
   }
   ```
   - **Output**: application/json
   ```json
   {
     "message": "Login successful",
     "token": "mock-jwt-token-123"
   }
   ```

5. **get-user-profile**
   - **HTTP Method & Route**: GET /get-user-profile
   - **Input**: None
   - **Output**: application/json
   ```json
   {
     "id": 1,
     "username": "nickiminaj",
     "email": "nickiminaj@gmail.com",
     "first_name": "Nicki",
     "last_name": "Minaj"
   }
   ```

6. **update-user-profile**
   - **HTTP Method & Route**: POST /update-user-profile
   - **Input**: application/json
   ```json
   {
     "email": "newemail@example.com",
     "first_name": "Onika",
     "last_name": "Maraj"
   }
   ```
   - **Output**: application/json
   ```json
   {
     "message": "Profile updated successfully",
     "updated_profile": {
       "id": 1,
       "username": "nickiminaj",
       "email": "newemail@example.com",
       "first_name": "Onika",
       "last_name": "Maraj"
     }
   }
   ```

## file listings.py

7. **get-all-listings**
   - **HTTP Method & Route**: GET /get-all-listings
   - **Input**: None
   - **Output**: application/json
   ```json
   {
     "listings": [
       {
         "id": 1,
         "title": "MacBook Pro 13-inch",
         "description": "Gently used MacBook Pro, perfect for students",
         "price": 800.00,
         "category": "Electronics",
         "condition": "Good",
         "seller_id": 1,
         "seller_name": "John Doe",
         "location": "Campus Library",
         "date_posted": "2024-10-15",
         "status": "available",
         "images": ["macbook1.jpg", "macbook2.jpg"]
       }
     ],
     "total_count": 1
   }
   ```

8. **post-listing**
   - **HTTP Method & Route**: POST /post-listing
   - **Input**: application/json
   ```json
   {
     "title": "iPhone 12",
     "description": "Barely used iPhone 12 in excellent condition",
     "price": 500.00,
     "category": "Electronics",
     "condition": "Excellent",
     "seller_id": 1,
     "seller_name": "John Doe",
     "location": "Student Center",
     "images": ["phone1.jpg"]
   }
   ```
   - **Output**: application/json
   ```json
   {
     "message": "Listing created successfully",
     "listing": {
       "id": 5,
       "title": "iPhone 12",
       "description": "Barely used iPhone 12 in excellent condition",
       "price": 500.00,
       "category": "Electronics",
       "condition": "Excellent",
       "seller_id": 1,
       "seller_name": "John Doe",
       "location": "Student Center",
       "date_posted": "2024-10-27",
       "status": "available",
       "images": ["phone1.jpg"]
     }
   }
   ```

9. **get-my-listings**
   - **HTTP Method & Route**: GET /get-my-listings
   - **Input**: 
     - Query Parameters:
       - `user_id` (integer, required): ID of the current user
   - **Output**: application/json
   ```json
   {
     "listings": [
       {
         "id": 1,
         "title": "MacBook Pro 13-inch",
         "price": 800.00,
         "status": "available",
         "date_posted": "2024-10-15"
       }
     ],
     "total_count": 1,
     "user_id": 1
   }
   ```

10. **get-item-listing**
    - **HTTP Method & Route**: GET /get-item-listing
    - **Input**: None
    - **Output**: application/json
    ```json
    [
      {
        "id": 1,
        "UserID": "John Doe",
        "item_name": "Laptop",
        "description": "Acer 15 inch laptop",
        "price": 1000.0,
        "picture": "pic URL",
        "bids": "Bids"
      }
    ]
    ```

## file purchases.py

11. **get-recent-purchases**
    - **HTTP Method & Route**: GET /get-recent-purchases
    - **Input**: None
    - **Output**: application/json
    ```json
    {
      "purchases": [
        {
          "id": 2,
          "title": "Calculus Textbook",
          "description": "Calculus: Early Transcendentals 8th Edition",
          "price": 75.00,
          "category": "Books",
          "condition": "Like New",
          "seller_id": 2,
          "seller_name": "Jane Smith",
          "location": "Student Center",
          "date_purchased": "2024-10-20",
          "status": "unclaimed",
          "images": ["textbook1.jpg"]
        }
      ],
      "total_count": 1
    }
    ```

12. **get-upcoming-pickups**
    - **HTTP Method & Route**: GET /get-upcoming-pickups
    - **Input**: None
    - **Output**: application/json
    ```json
    {
      "pickups": [
        {
          "id": 2,
          "title": "Calculus Textbook",
          "description": "Calculus: Early Transcendentals 8th Edition",
          "price": 75.00,
          "category": "Books",
          "condition": "Like New",
          "seller_id": 2,
          "seller_name": "Jane Smith",
          "location": "Student Center",
          "date_purchased": "2024-10-20",
          "status": "unclaimed",
          "images": ["textbook1.jpg"]
        }
      ],
      "total_count": 1
    }
    ```

**Data Types:**
- `id`: integer
- `title`: string
- `description`: string
- `price`: number (float)
- `category`: string
- `condition`: string
- `seller_id`: integer
- `seller_name`: string
- `location`: string