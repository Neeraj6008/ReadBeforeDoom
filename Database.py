import pymysql as pms
from pymysql.cursors import DictCursor
import hashlib
import json

# This function checks if the entered link is already in a mysql_database or not, if yes, returns the prestored analysis results
# and if not, continues to the next function.
def sql_cache_check(link):
    try:
        connect = pms.connect(
            host='localhost', 
            user='root', 
            password='MySQL_Neeraj@25', 
            db='tc_analysis',
            cursorclass=DictCursor
        )
        cursor = connect.cursor()

        url_hash = hashlib.sha256(link.encode()).hexdigest()

        cursor.execute('SELECT * FROM tc_analysis_results WHERE url_hash = %s;', (url_hash,))
        result = cursor.fetchone()

        cursor.close()
        connect.close()

        if result:
            # Parse JSON strings back to lists/dicts if needed
            suspicious_clauses = result.get('suspicious_clauses', '[]')
            if isinstance(suspicious_clauses, str):
                try:
                    suspicious_clauses = json.loads(suspicious_clauses)
                except json.JSONDecodeError:
                    suspicious_clauses = []
            
            return {
                'link_in_db': True,
                'url': result['url'],
                'safety_rating': result.get('safety_rating', 'Unknown'),
                'suspicious_clauses': suspicious_clauses,
                'recommendation': result.get('recommendation', 'Analysis pending')
            }
        else:
            return {
                'link_in_db': False
            }
    except Exception as e:
        print(f"Database error: {e}")
        return {'link_in_db': False}

# After the T&C analysis, the results will be stored in the MySQL database.
def store_analysis_result(url, tc_text, analysis_result):
    try:
        connect = pms.connect(
            host='localhost', 
            user='root', 
            password='MySQL_Neeraj@25', 
            db='tc_analysis',
            cursorclass=DictCursor
        )
        cursor = connect.cursor()
        
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        tc_hash = hashlib.sha256(tc_text.encode()).hexdigest()
        
        # Extract domain from URL more safely
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            domain = parsed_url.netloc or url.split('/')[2] if '/' in url else url
        except:
            domain = url
        
        # Ensure all required fields are present
        suspicious_clauses = analysis_result.get('suspicious_clauses', [])
        safety_rating = analysis_result.get('safety_rating', '0/10')
        recommendation = analysis_result.get('recommendation', 'No analysis available')
        risk_categories = analysis_result.get('risk_categories', [])
        
        # Convert lists to JSON strings for storage
        if isinstance(suspicious_clauses, list):
            suspicious_clauses_json = json.dumps(suspicious_clauses)
        else:
            suspicious_clauses_json = str(suspicious_clauses)
        
        if isinstance(risk_categories, list):
            risk_categories_json = json.dumps(risk_categories)
        else:
            risk_categories_json = str(risk_categories)
        
        # Check if record already exists
        cursor.execute('SELECT id FROM tc_analysis_results WHERE url_hash = %s', (url_hash,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing record
            update_query = """
            UPDATE tc_analysis_results 
            SET url = %s, domain = %s, tc_text_hash = %s, tc_length = %s, 
                suspicious_clauses = %s, safety_rating = %s, recommendation = %s, 
                risk_categories = %s, updated_at = NOW()
            WHERE url_hash = %s
            """
            cursor.execute(update_query, (
                url, domain, tc_hash, len(tc_text),
                suspicious_clauses_json, safety_rating, recommendation,
                risk_categories_json, url_hash
            ))
            print("Updated existing database record")
        else:
            # Insert new record
            insert_query = """
            INSERT INTO tc_analysis_results 
            (url, url_hash, domain, tc_text_hash, tc_length, suspicious_clauses, 
            safety_rating, recommendation, risk_categories, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            cursor.execute(insert_query, (
                url, url_hash, domain, tc_hash, len(tc_text),
                suspicious_clauses_json, safety_rating, recommendation,
                risk_categories_json
            ))
            print("Inserted new database record")
        
        connect.commit()
        cursor.close()
        connect.close()
        
        return {
            'success': True,
            'message': 'Analysis result stored successfully'
        }
        
    except Exception as e:
        print(f"Database storage error: {e}")
        return {
            'success': False,
            'message': f"Error storing to database: {e}"
        }

# Optional: Function to create the database table if it doesn't exist
def create_table_if_not_exists():
    """
    Creates the tc_analysis_results table if it doesn't exist.
    Run this once to set up your database schema.
    """
    try:
        connect = pms.connect(
            host='localhost', 
            user='root', 
            password='MySQL_Neeraj@25', 
            db='tc_analysis'
        )
        cursor = connect.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS tc_analysis_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            url VARCHAR(500) NOT NULL,
            url_hash VARCHAR(64) UNIQUE NOT NULL,
            domain VARCHAR(255),
            tc_text_hash VARCHAR(64),
            tc_length INT,
            suspicious_clauses TEXT,
            safety_rating VARCHAR(10),
            recommendation TEXT,
            risk_categories TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_url_hash (url_hash),
            INDEX idx_domain (domain)
        )
        """
        
        cursor.execute(create_table_query)
        connect.commit()
        cursor.close()
        connect.close()
        print("Database table created successfully (or already exists)")
        
    except Exception as e:
        print(f"Error creating table: {e}")

if __name__ == "__main__":
    # Run this to create the table structure
    create_table_if_not_exists()