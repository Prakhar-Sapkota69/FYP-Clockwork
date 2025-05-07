from PySide6.QtWidgets import QMessageBox, QInputDialog
import psutil
import os

class SystemOptimizer:
    @staticmethod
    def get_system_usage():
        """
        Get CPU, RAM, and Disk usage as percentages.
        """
        try:
            # Warm-up call to get accurate CPU readings
            psutil.cpu_percent(interval=None)
            
            # Get CPU usage with a 1-second interval to match Task Manager
            cpu_usage = psutil.cpu_percent(interval=1.0, percpu=False)
            
            # Get RAM usage
            ram = psutil.virtual_memory()
            ram_usage = ram.percent
            
            # Get Disk activity instead of disk space usage
            disk_io = psutil.disk_io_counters()
            disk_activity = (disk_io.read_bytes + disk_io.write_bytes) / (1024 * 1024)  # Convert to MB
            
            # Print debug information
            print(f"CPU Usage: {cpu_usage:.2f}%")
            print(f"RAM Usage: {ram_usage:.2f}%")
            print(f"Disk Activity: {disk_activity:.2f} MB/s")
            
            return cpu_usage, ram_usage, disk_activity
        
        except Exception as e:
            print(f"Error getting system usage: {e}")
            return 0, 0, 0

    @staticmethod
    def optimize_pc():
        """
        Delete temporary files to optimize the system.
        Returns the number of deleted files.
        """
        temp_dirs = [
            os.getenv('TEMP'),  # Windows temporary files
            os.getenv('TMP'),   # Alternative Windows temporary files
            '/tmp',             # Linux/Mac temporary files
        ]

        deleted_files = 0
        for temp_dir in temp_dirs:
            if temp_dir and os.path.exists(temp_dir):
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            os.remove(file_path)
                            deleted_files += 1
                        except Exception as e:
                            print(f"Failed to delete {file_path}: {e}")
        return deleted_files

    @staticmethod
    def get_unnecessary_processes(cpu_threshold=50, memory_threshold=70):
        """
        Identify background processes consuming excessive CPU or memory.
        """
        unnecessary_processes = []
        system_processes = {
            "explorer.exe", "csrss.exe", "winlogon.exe", "system", "taskmgr.exe",
            "system idle process", "idle"
        }  # Safe list

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                name = proc.info['name'].lower()
                pid = proc.info['pid']
                cpu = proc.info['cpu_percent']
                memory = proc.info['memory_percent']
                if (
                    (cpu > cpu_threshold or memory > memory_threshold)
                    and name not in system_processes
                    and pid != 0
                ):
                    unnecessary_processes.append((pid, proc.info['name'], cpu, memory))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return unnecessary_processes

    @staticmethod
    def close_unnecessary_processes():
        """
        Ask user confirmation before closing high CPU/memory processes.
        """
        processes = SystemOptimizer.get_unnecessary_processes()
        if not processes:
            QMessageBox.information(None, "No Processes", "No unnecessary processes found.")
            return

        process_list = "\n".join([f"{idx}. {name} (PID: {pid}) - CPU: {cpu:.2f}%, Memory: {mem:.2f}%" 
                                    for idx, (pid, name, cpu, mem) in enumerate(processes, start=1)])

        # Prompt user to input process numbers
        input_dialog = QInputDialog()
        input_text, ok = input_dialog.getText(None, "Unnecessary Processes",
                                              f"Unnecessary processes consuming high CPU/Memory:\n{process_list}\n\n"
                                              "Enter the numbers of the processes you want to close (comma-separated), or 'all' to close all:")

        if not ok or not input_text:
            return  # User canceled or didn't enter anything

        if input_text.lower() == 'all':
            to_kill_indices = range(1, len(processes) + 1)
        else:
            try:
                to_kill_indices = [int(i) for i in input_text.split(',') if i.strip().isdigit()]
            except ValueError:
                QMessageBox.warning(None, "Invalid Input", "Invalid input. No processes were terminated.")
                return

        for idx in to_kill_indices:
            if 1 <= idx <= len(processes):
                pid = processes[idx - 1][0]
                try:
                    psutil.Process(pid).terminate()
                    QMessageBox.information(None, "Process Terminated", f"Terminated {processes[idx - 1][1]} (PID: {pid})")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    QMessageBox.warning(None, "Termination Failed", f"Failed to terminate process with PID {pid}")
