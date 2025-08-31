import pymysql as pms
from pymysql.cursors import DictCursor
import hashlib


# This function checks if the entered link is already in a mysql_database or not, if yes, returns the prestored analysis results
# and if not, continues to the next function.
def sql_cache_check(link):
    try:
        connect = pms.connect(
            host='localhost', 
            user='root', 
            password='MySQL_Neeraj@25', 
            db='tc_analysis',
            cursorclass=DictCursor  # This is an Out of syllabus thing, returns dictionaries.
        )
        cursor = connect.cursor()

        url_hash = hashlib.sha256(link.encode()).hexdigest()

        cursor.execute('SELECT * FROM tc_analysis_results WHERE url_hash = %s;', (url_hash,))
        # Hash is unique for each link, so uses fetchone()
        result = cursor.fetchone()

        cursor.close()
        connect.close()

        # returns a dictionary 
        if result:
            return {
                'link_in_db': True,
                'url': result['url'],
                'safety_rating': result.get('safety_rating', 'Unknown'),
                'suspicious_clauses': result.get('suspicious_clauses', []),
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
        domain = url.split('/')[2]  # Extract domain from URL
        
        insert_query = """
        INSERT INTO tc_analysis_results 
        (url, url_hash, domain, tc_text_hash, tc_length, suspicious_clauses, 
        safety_rating, recommendation, risk_categories) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            url,
            url_hash,
            domain,
            tc_hash,
            len(tc_text),
            analysis_result['suspicious_clauses'],  # JSON string
            analysis_result['safety_rating'],       # 1-10 score
            analysis_result['recommendation'],      # Accept/reject advice
            analysis_result['risk_categories']      # JSON string
        ))
        
        connect.commit()
        cursor.close()
        connect.close()
    
    except Exception as e:
        return {
            'success' : False,
            'message' : f"There is an error connecting to the database: {e}"
        }