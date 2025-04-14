import paramiko
import getpass

def block_network_traffic(ssh, password, ssh_port):
    try:
        commands = [
            "ufw disable",
            f"iptables -A INPUT -p tcp --dport {ssh_port} -j ACCEPT",
            f"iptables -A OUTPUT -p tcp --sport {ssh_port} -j ACCEPT",
            "iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT",
            "iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT",
            "iptables -A INPUT -j DROP",
            "iptables -A OUTPUT -j DROP"
        ]
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(f"sudo -S {cmd}", get_pty=True)
            stdin.write(password + '\n')
            stdin.flush()
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                error = stderr.read().decode()
                print(f"FAILED: {cmd}\nError: {error}")
            else:
                print(f"SUCCESS: {cmd}")
    except Exception as e:
        print(f"Critical error: {str(e)}")

def unblock_network_traffic(ssh, password):
    try:
        commands = ["iptables -F"]
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(f"sudo -S {cmd}", get_pty=True)
            stdin.write(password + '\n')
            stdin.flush()
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                print(f"FAILED: {cmd}\nError: {stderr.read().decode()}")
            else:
                print(f"SUCCESS: {cmd}")
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    # SSH connection details
    vm_ip = input("Enter VM IP: ")
    ssh_port = int(input("Enter SSH port (default 22): ") or 22)
    username = input("Enter SSH username: ")
    password = getpass.getpass("Enter SSH password: ")

    # Initialize SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to VM with custom SSH port
        ssh.connect(vm_ip, port=ssh_port, username=username, password=password, timeout=10)
        print(f"Connected to VM on port {ssh_port}.")

        action = input("Block or Unblock traffic? (block/unblock): ").strip().lower()
        sudo_password = getpass.getpass("Enter VM sudo password: ")

        if action == "block":
            block_network_traffic(ssh, sudo_password, ssh_port)
            print("Network traffic blocked. SSH port remains open.")
        elif action == "unblock":
            unblock_network_traffic(ssh, sudo_password)
            print("Network traffic unblocked. Firewall rules reset.")
        else:
            print("Invalid action. Use 'block' or 'unblock'.")

    except paramiko.AuthenticationException:
        print("Authentication failed. Check credentials.")
    except paramiko.SSHException as e:
        print(f"SSH error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        ssh.close()
        print("Disconnected.")

if __name__ == "__main__":
    main()