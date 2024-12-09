import paramiko
import sqlite3
import uuid  # To generate unique session IDs
import socket
import random
import os
import logging
import traceback
from ollama import Client
import sys
import json


# Configure logging
session_id = str(uuid.uuid4())
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def log_credentials(username, password, session_id):
    conn = sqlite3.connect('honeypot_credentials.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO login_attempts (username, password, session_id) VALUES (?, ?, ?)
    ''', (username, password, session_id))
    conn.commit()
    conn.close()


def create_db():
    conn = sqlite3.connect('honeypot_credentials.db')
    cursor = conn.cursor()
    # Create a table to store username and password (if not exists)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS login_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        session_id TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()


class MySSHHandler(paramiko.ServerInterface):
    def check_auth_password(self, username, password):
        logging.info(f"Authentication attempt: username={username}, password={password}")
        log_credentials(username, password, session_id)
        logging.info("Saved credentials to DB")
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        return True

class SSHServer:
    def __init__(self, host, port, key_filename):
        self.host = host
        self.port = port
        self.key_filename = key_filename
        self.transport = None
        self.username = ''
        self.password = ''
        self.computer = ''
        self.current_directory = f'/home/{self.username}'
        self.sudo_ability = True
        self.session_id = session_id
        self.banner_sent = False
        self.industry = ''
        self.client_ip = None
        self.distro = None

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(100)
#        logging.info(f"Listening on {self.host}:{self.port}")

        private_key = paramiko.RSAKey(filename=self.key_filename)

        while True:
            client_socket, client_addr = server_socket.accept()
            self.client_ip = client_addr[0]  # Get the client's IP address
            logging.info(f"Connection from {client_addr}")
            
            self.session_id = str(uuid.uuid4())  # Generate a unique session ID

            self.transport = paramiko.Transport(client_socket)
            self.transport.add_server_key(private_key)
            server = MySSHHandler()
            self.transport.start_server(server=server)

            channel = self.transport.accept(20)
            if channel is None:
                continue
            self.username = self.transport.get_username()
            self.current_directory = f'/home/{self.username}'
            logging.info(f"password: {self.password}")

            try:
                self.handle_client(channel)
            except Exception as e:
                logging.error(f"Error handling client: {e}")
                logging.error(traceback.format_exc())

            finally:
                channel.close()
                logging.info("Connection closed.")


    def generate_domain(self):
        prompt = f"""generate a domain to be used in a bash terminal\n
        You should return a string that looks like a domain name and only that.
        Make it creative, unique and memorable related to {self.industry}. 
        Do not use the words like example or test or demo.
        You can include the words staging or production, or prod.
        Pick one option one, do not offer suggestions as its being used to generate the banner.
        The output should only have one option, no buts, or:
        subdomain.domain.com
        """
        domain = send_to_llm(prompt)
        self.computer = domain.replace('"', '')
        self.computer = self.computer.strip().lower()
        logging.info(f'Domain is set to {self.computer}')
        return



    def pick_industry(self):
        industry_list = [
            'Technology', 
            'Finance', 
            'Government', 
            'Media', 
            'Retail', 
            'Aerospace', 
            'Healthcare', 
            'Telecommunications', 
            'Transportation', 
            'Energy', 
            'Construction', 
            'Manufacturing', 
            'Agriculture', 
            'Defense'
        ]
        
        selected_industry = random.choice(industry_list)
        self.industry = selected_industry
        logging.info(f'Industry is set to {self.industry}')
        return

    def handle_client(self, channel):
        # Send banner once
        self.pick_industry()
        self.generate_domain()
        self.get_static_banner()
        banner_output = self.generate_banner()
        

        channel.send(banner_output+ "\n")
        if not self.banner_sent:  # Check if the banner has been sent already
            self.store_banner(banner_output)  
            self.banner_sent = True  # Set the flag to prevent saving the banner again
        channel.send(f"{self.username}@{self.computer}:{self.current_directory}$ ")
        while True:
            try:
                command = channel.recv(1024).decode('utf-8').strip()
                if not command:
                    channel.send(f"{self.username}@{self.computer}:{self.current_directory}$ ")
                    continue
                else:
                    logging.info(f"Received command: {command}")
                    response = self.process_command(command)
                    self.store_command_response(self.username, command, response)
                    channel.send(f"{response}")
                    channel.send(f"{self.username}@{self.computer}:{self.current_directory}$ ")
#                    channel.send(f"{self.username}@{self.computer}:{self.current_directory}$ {response}\n")
#                    channel.send(f"{self.username}@{self.computer}:{self.current_directory}$ ")
                if command == 'exit':
                    break

            except Exception as e:
                logging.error(f"Client disconnected or error occurred: {e}")
                break

    def store_banner(self, banner):
        """ Store the banner in the database only once for the session. """
        try:
            conn = sqlite3.connect('ssh_logs.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO logs (username, password, command, response, industry, ip_address, session_id) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.username, self.password, 'banner', banner, self.industry, self.client_ip, self.session_id))
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Error storing banner in DB: {e}")


    def store_command_response(self, username, command, response):
        """ Store the command, response, IP address, and session ID in the database. """
        try:
            conn = sqlite3.connect('ssh_logs.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO logs (username, password, command, response, ip_address, session_id) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, self.password, command, response, self.client_ip, self.session_id))
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Error storing command/response in DB: {e}")



    def process_command(self, command):
        if command.startswith('cd'):
            self.current_directory = self.change_directory(command)
            return f"{self.current_directory}\n"
        elif command.startswith('ls') and len(command.split()) < 3 and not command[-1].endswith('/'):
            command += f' {self.current_directory}/'

            logging.info(f"Command: {command}")
            return self.handle_general_command(command)
        elif command == 'whoami':
            return f"{self.username}\n"
        elif command == 'pwd':
            return f"{self.current_directory}\n"
        elif command.startswith('sudo'):
            return self.handle_sudo_command(command)
        else:
            return self.handle_general_command(command)

    def handle_sudo_command(self, command):
        if self.sudo_ability and command.endswith('-i'):
            self.username = 'root'
            self.current_directory = '/root'
            return f"Switched to root user.\n"
        else:
            prompt = f""""""
            return self.get_llm_response(command)

    def handle_general_command(self, command):
        output_llm = self.get_llm_response(command)
        return f"{self.username}@{self.computer}:{self.current_directory}$ {output_llm}\n"

    def change_directory(self, command):
        target_dir = command[3:].strip()
        if target_dir.startswith('/'):
            return target_dir
        elif target_dir == '../':
            return '/'.join(self.current_directory.rstrip('/').split('/')[:-1]) or '/'
        elif target_dir == '~':
            return f"/home/{self.username}"
        else:
            return os.path.normpath(os.path.join(self.current_directory, target_dir))

    def get_llm_response(self, command):
        try:
            prompt = self.format_prompt(command)
            return send_to_llm(prompt)
        except Exception as e:
            logging.error(f"Error generating LLM response: {e}")
            return "Command failed."

    def get_static_banner(self):
        linux_distros = [
            "Ubuntu",
            "Debian",
            "Red Hat Enterprise Linux",
            "CentOS",
            "Fedora",
        ]

        self.distro = random.choice(linux_distros)
        return 

    def generate_banner(self):
        prompt = f"""Generate a linux banner for {self.distro} for the entreprise {self.computer}\nIn the following industry {self.industry}\n"""
        logging.info(f"Banner generated will be {self.distro} for {self.computer}")
        
        response = send_to_llm(prompt)
        return response + '\n'
        

    def format_prompt(self, command):
        return f"""
            You are a Linux terminal running {self.distro} running as {self.username}.\n
            Ensure that the response only includes the direct output of the command, mimicking a real terminal.\n
            - Do not add any explanations, commentary, or additional information.\n
            - Do not provide any notes, clarification, or mimicked responses beyond the terminal output.\n
            - Throw an error if the command is invalid for {self.distro}.\n
            - Throw an error if the command is requires root and username is not root.\n
            - The command is: {command}
            """
#            f"""You are a Linux terminal for {self.distro}.
#            Ensure the response mimics a real terminal output.\n
#            Do not add commentary after outputting the command.\n
#            Do not provide any notes mimicking the command.\n
#            Do not provide explanation of output 
#            Do not explanation of command.\n
#            Do not indicate any information about the command.\n
 #           Do not provide any notes mimicking the response.\n 
#            The command is below: \n
#            {command}
#            """
        

def send_to_llm(prompt):
    if config['llm_provider'] == 'ollama':
        try:
            model = config['llm_model']
            host = f"{config['llm_ip']}:{config['port']}"
            client = Client(host=host)
            response = client.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
            return '\n'+ response.get('message', {}).get('content', 'Error communicating with LLM').replace("```","")
        except Exception as e:
            logging.error(f"Error communicating with LLM: {e}")
            return "Error communicating with LLM."
    else:
        return "Other providers have not been set"
    


def create_database():
    conn = sqlite3.connect('ssh_logs.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password, TEXT,
            command TEXT,
            response TEXT,
            banner TEXT,
            industry TEXT,
            ip_address TEXT,
            session_id TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()




if __name__ == "__main__":
    with open('config.json', 'r') as configuration_file:
        config = json.load(configuration_file)
    
    
    host = config["listen"]
    port = config["ssh_port"]
    database = config["database"]
    
    key_filename = "server_rsa.key"
    
    if not os.path.exists(key_filename):
        key = paramiko.RSAKey.generate(2048)
        key.write_private_key_file(key_filename)
    
    if database == 'sqlite':
        create_database()  # Initialize the database
        create_db()
    logging.info(f'Starting LLM Honey on {host}:{port}\nSaving details to {database}')
    ssh_server = SSHServer(host, port, key_filename)
    ssh_server.start()
