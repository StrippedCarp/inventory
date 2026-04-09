from app import create_app

# Use SQLite for local development if PostgreSQL not available
app = create_app(use_sqlite=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)