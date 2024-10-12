import logging
from flask import Flask, request, jsonify, render_template
import oracledb

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)  
logging.info('Flask application has started')
pw = "Hackathon12345678"

dsn_str = "(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1521)(host=adb.ap-mumbai-1.oraclecloud.com))(connect_data=(service_name=gd110a4c34fbb2c_hackathon_low.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))"

# Oracle connection function
def get_db_connection():
    logging.info('Establishing connection to Oracle DB')
    return oracledb.connect(
        user="admin",
        password=pw,
        dsn=dsn_str
    )

@app.route('/')
def index():
    return render_template('Poll.html') 

# Route to accept the query vector and return result
@app.route('/query', methods=['POST'])
def query_sea_animal():
    query_data = request.json
    query_vector = query_data.get('vector')

    logging.info(f"Received query vector: {query_vector}")

    if not query_vector:
        logging.error("Query vector not provided")
        return jsonify({"error": "Query vector not provided"}), 400

    query_vector_str = str(query_vector)
    sql_query = f"""
        SELECT id, name, VECTOR_DISTANCE(embedding, '{query_vector_str}') AS similarity
        FROM SEA_ANIMALS ma
        ORDER BY similarity ASC
        FETCH FIRST 1 ROWS ONLY
    """
    # sql_query = "SELECT * FROM SEA_ANIMALS"
    logging.info(f"Executing SQL query: {sql_query}")

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(sql_query)
    row = cursor.fetchone()
    logging.info(f"Query result: {row}")
    # print(row)

    cursor.close()
    connection.close()

    if row:
        logging.info(f"Returning result: ID={row[0]}, Name={row[1]}")
        return jsonify({"id": row[0], "name": row[1]})
    else:
        logging.warning("No matching records found")
        return jsonify({"error": "No matching records found"}), 404

if __name__ == '__main__':
    logging.info("Starting Flask app")
    app.run(debug=False, host='0.0.0.0', port=5001)
