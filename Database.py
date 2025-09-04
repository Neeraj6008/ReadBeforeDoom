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
            db='tc_analysis'
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
        cursor.execute('SELECT * FROM tc_analysis_results WHERE url_hash = %s', (url_hash,))
        existing = cursor.fetchone()
        
        if existing:
            print("Record already exists in database, skipping...")
            cursor.close()
            connect.close()
            return {
                'success': True,
                'message': 'Record already exists'
            }
        
        # Extract just the number from safety_rating (e.g., "4/10" -> "4")
        if "/" in safety_rating:
            safety_rating_short = safety_rating.split("/")[0]
        else:
            safety_rating_short = safety_rating[:2]  # Just in case
        
        # Simple insert query without updated_at column
        insert_query = """
        INSERT INTO tc_analysis_results 
        (url, url_hash, domain, tc_text_hash, tc_length, suspicious_clauses, 
        safety_rating, recommendation, risk_categories) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            url, url_hash, domain, tc_hash, len(tc_text),
            suspicious_clauses_json, safety_rating_short, recommendation,
            risk_categories_json
        ))
        
        connect.commit()
        cursor.close()
        connect.close()
        
        print("New record inserted successfully")
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

if __name__ == "__main__":
    print("Database module loaded. Your existing table structure will be used.")