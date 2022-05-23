import sqlite3
def do_database(query):
    """
    This function is used to connect to the database and run a query.
    """
    try:
        # Connect to the database
        connection = sqlite3.connect('database.db')
        # Create a cursor object
        cursor = connection.cursor()
        # Execute the query
        cursor.execute(query)
        # commit changes
        connection.commit()
        # Fetch the results
        results = cursor.fetchall()
        # Close the connection
        # Return the results
        return results
    except:
        # If there was an error, return an empty list
        return []
    finally:
        # Close the cursor object
        cursor.close()
        # Close the connection
        connection.close()