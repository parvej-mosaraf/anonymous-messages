# Anonymous Messages Platform

A secure web application that allows users to receive anonymous messages through a unique, shareable link. Built with Flask, MongoDB, and modern web technologies.

## Features

- 🔐 **Secure Authentication**
  - 6-digit PIN-based authentication
  - Secure password hashing using Werkzeug
  - Session-based user management

- 🔒 **Message Security**
  - End-to-end message encryption
  - Messages are encrypted using recipient's credentials
  - Only message owners can decrypt and view their messages
  - Secure data storage in MongoDB Atlas

- 🎯 **User-Friendly Interface**
  - Clean, modern UI using Tailwind CSS
  - Responsive design for all devices
  - Intuitive message management dashboard

- 📱 **Easy Message Sharing**
  - Generate unique, shareable links
  - One-click link copying
  - Anonymous message submission

## System Architecture

```mermaid
graph TD
    A[User] -->|Register/Login| B[Authentication]
    B -->|Valid Credentials| C[Dashboard]
    C -->|Generate| D[Unique Link]
    D -->|Share| E[Anonymous Sender]
    E -->|Submit| F[Message System]
    F -->|Encrypt| G[MongoDB Atlas]
    G -->|Decrypt| H[Message View]
    H -->|Display| C

    subgraph "Database Layer"
        G -->|Users Collection| I[User Data]
        G -->|Messages Collection| J[Encrypted Messages]
    end
```

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant App
    participant MongoDB
    participant Render

    User->>App: Register/Login
    App->>MongoDB: Store/Verify User Data
    MongoDB-->>App: User Data
    App-->>User: Dashboard Access

    User->>App: Generate Link
    App->>MongoDB: Store User ID
    App-->>User: Shareable Link

    Anonymous->>App: Send Message
    App->>MongoDB: Store Encrypted Message
    MongoDB-->>App: Confirmation
    App-->>Anonymous: Success

    User->>App: View Messages
    App->>MongoDB: Fetch Messages
    MongoDB-->>App: Encrypted Messages
    App->>App: Decrypt Messages
    App-->>User: Display Messages
```

## Security Features

1. **PIN Security**
   - 6-digit numeric PIN requirement
   - Secure hashing using Werkzeug's security functions
   - Protection against brute force attacks

2. **Message Encryption**
   - Messages encrypted using recipient's credentials
   - Fernet symmetric encryption
   - Secure key generation and management

3. **Database Security**
   - MongoDB Atlas cloud database
   - Encrypted data at rest
   - Secure connection strings
   - IP whitelisting
   - Role-based access control

4. **Session Management**
   - Secure session handling
   - Automatic session expiration
   - Protection against session hijacking

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/anonymous-messages.git
cd anonymous-messages
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up MongoDB:
   - Create a MongoDB Atlas account
   - Create a new cluster
   - Set up database user and network access
   - Get your connection string

5. Create .env file:
```
MONGODB_URI=your_mongodb_connection_string
```

6. Run the application:
```bash
python app.py
```

## Project Structure

```
anonymous-messages/
├── app.py              # Main application file
├── requirements.txt    # Project dependencies
├── .env               # Environment variables
├── static/            # Static files (CSS, JS)
├── templates/         # HTML templates
│   ├── index.html    # Landing page
│   ├── login.html    # Login page
│   ├── register.html # Registration page
│   ├── dashboard.html # User dashboard
│   ├── message.html  # Message submission page
│   └── view.html     # Message viewing page
```

## Database Schema

### Users Collection
```json
{
    "username": "string",
    "password": "hashed_string",
    "user_id": "uuid_string"
}
```

### Messages Collection
```json
{
    "id": "uuid_string",
    "user_id": "uuid_string",
    "content": "encrypted_string",
    "timestamp": "datetime_string"
}
```

## Deployment

The application is deployed on Render with the following setup:

1. **Environment Variables**
   - `MONGODB_URI`: MongoDB Atlas connection string
   - `SECRET_KEY`: Flask session secret key

2. **Build Command**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Command**
   ```bash
   gunicorn app:app
   ```

## Usage

1. **Registration**
   - Create an account with username and 6-digit PIN
   - PIN must be exactly 6 digits (0-9)

2. **Dashboard**
   - Generate your unique message link
   - View message count and access messages
   - Copy and share your link

3. **Receiving Messages**
   - Share your unique link
   - Others can send anonymous messages
   - Messages are automatically encrypted and stored in MongoDB

4. **Viewing Messages**
   - Access your messages through the dashboard
   - Messages are automatically decrypted
   - View message history with timestamps

## Security Considerations

- All PINs are stored as secure hashes in MongoDB
- Messages are encrypted using recipient's credentials
- MongoDB Atlas provides encrypted data at rest
- Session management with secure cookies
- Protection against common web vulnerabilities

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Flask web framework
- MongoDB Atlas for database
- Tailwind CSS for styling
- Werkzeug for security features
- Cryptography library for message encryption
- Render for hosting 