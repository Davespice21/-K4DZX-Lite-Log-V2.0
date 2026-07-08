import datetime
import os
import re

# David Spicer k4DZX
# K4DZX Lite Radio Log V2.0

class Log:
    def __init__(self, number, call, freq, time_str, signalstrength):
        self.number = number
        self.call = call
        self.freq = freq
        self.time = time_str
        self.signalstrength = signalstrength

    def __str__(self):
        return f"{self.number:>2} {self.call:>20} {self.freq:>20} {self.signalstrength:>25} {self.time:>35}"


def clear_screen():
    """Clear terminal screen for clean interface"""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_current_utc_time():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%H%M")


def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', "_", name.strip())
    return name[:100]


def get_log_filename(event):
    if event and event.strip():
        return f"{sanitize_filename(event)}.txt"
    return "contacts.txt"


def load_logs(filename):
    logs = []
    next_number = 1
    try:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                lines = f.readlines()
                for line in lines[1:]:
                    if line.strip():
                        parts = line.strip().split(maxsplit=4)
                        if len(parts) >= 5:
                            try:
                                number = int(parts[0])
                                call = parts[1]
                                freq = parts[2]
                                ss = parts[3]
                                time_str = parts[4]
                                logs.append(Log(number, call, freq, time_str, ss))
                            except:
                                continue
            if logs:
                next_number = max((log.number for log in logs), default=0) + 1
            print(f";) Loaded {len(logs)} contacts from {filename}")
        else:
            print(f" New log: {filename}")
    except Exception as e:
        print(f"Warning Load Error: {e}")
    input("Press Enter to continue...")
    return logs, next_number


def save_logs(logs, filename):
    try:
        with open(filename, "w") as f:
            f.write(f"{'Log Number:':>2} {'Call Sign:':>20} {'Frequency:':>20} {'Signal Strength:':>25} {'Time (UTC):':>35}\n")
            for log in logs:
                f.write(str(log) + "\n")
        print(f";) Saved to {filename}")
        input("Press Enter to continue...")
    except Exception as e:
        print(f"XXXXXX Save failed XXXXXXXX: {e}")
        input("Press Enter...")


def print_header(event, filename):
    clear_screen()
    print("=" * 110)
    print(" " * 35 + "K4DZX Lite Radio Log V 2.0")
    print("=" * 110)
    print(f"Event : {event if event else 'General Log'}")
    print(f"File  : {filename}")
    print("-" * 110)


def mainmenu(logs, event, filename):
    print_header(event, filename)
    print("1. Add Contact    2. Edit Contact    3. Delete Contact")
    print("4. Save Log Book       5. Load Log Book         6. New Log Book    7. Exit")
    print("-" * 110)
    print(f"{'Log #':>4} {'Call Sign':>20} {'Frequency':>20} {'Signal':>25} {'Time (UTC)':>35}")
    print("-" * 110)
    
    for log in logs:
        print(str(log))
    if not logs:
        print(" " * 45 + "(No contacts logged yet)")
    print("-" * 110)

    while True:
        try:
            choice = int(input("Select option: "))
            if 1 <= choice <= 7:
                return choice
        except ValueError:
            pass
        print("Please enter a number 1-7.")


def startup_menu():
    clear_screen()
    print("\n" + "="*65)
    print(" " * 18 + "K4DZX Lite Radio Log V2.0")
    print("="*65)
    print("1. Create New Log Book")
    print("2. Open Existing Log Book")
    print("3. Exit")
    print("="*65)
    
    while True:
        try:
            choice = int(input("\nChoose option: "))
            if choice in (1, 2, 3):
                return choice
        except ValueError:
            pass
        print("Please enter 1, 2 or 3.")


def add_contact(logs, next_number):
    clear_screen()
    print("--- Add New Contact ---")
    call = input("Call Sign: ").strip().upper()
    freq = input("Frequency: ").strip()
    
    default_time = get_current_utc_time()
    t = input(f"Time (UTC) [{default_time}]: ").strip()
    time_str = t if t else default_time
    
    ss = input("Signal Strength: ").strip()
    
    log = Log(next_number, call, freq, time_str, ss)
    logs.append(log)
    print(f";) Contact #{next_number} added successfully!")
    input("\nPress Enter to return to menu...")
    return logs, next_number + 1


# ====================== MAIN ======================
def main():
    choice = startup_menu()
    
    if choice == 3:
        print("73! See you next time.")
        return
    
    if choice == 1:  # New Log
        clear_screen()
        event = input("Enter Event Name: ").strip()
        filename = get_log_filename(event)
        logs = []
        next_number = 1
        print(f" New log book ready: {filename}")
        input("Press Enter to continue...")
    else:  # Open Existing
        clear_screen()
        print("Existing log files:")
        txt_files = [f for f in os.listdir(".") if f.lower().endswith(".txt")]
        if txt_files:
            for i, f in enumerate(txt_files, 1):
                print(f"  {i}. {f}")
            print("  0. Enter filename manually")
            try:
                sel = int(input("\nSelect number: "))
                filename = txt_files[sel-1] if sel != 0 else input("Filename: ").strip()
            except:
                filename = input("Filename: ").strip()
        else:
            filename = input("No logs found. Enter filename: ").strip()
        
        if not filename.endswith(".txt"):
            filename += ".txt"
        
        logs, next_number = load_logs(filename)
        event = filename[:-4] if filename != "contacts.txt" else ""

    # Main loop
    while True:
        selection = mainmenu(logs, event, filename)
        
        if selection == 1:
            logs, next_number = add_contact(logs, next_number)
        elif selection == 2:  # Edit
            clear_screen()
            print("--- Edit Contact ---")
            try:
                num = int(input("Log # to edit: "))
                for log in logs:
                    if log.number == num:
                        for field, attr in [("Call Sign", "call"), ("Freq", "freq"), ("Time", "time"), ("Signal", "signalstrength")]:
                            val = input(f"New {field} [{getattr(log, attr)}]: ").strip()
                            if val:
                                setattr(log, attr, val.upper() if field == "Call Sign" else val)
                        print(";) Contact updated!")
                        input("Press Enter...")
                        break
                else:
                    print("Not found.")
                    input("Press Enter...")
            except:
                print("Invalid input.")
                input("Press Enter...")
        elif selection == 3:  # Delete
            clear_screen()
            print("--- Delete Contact ---")
            try:
                num = int(input("Log # to delete: "))
                for i, log in enumerate(logs):
                    if log.number == num:
                        if input(f"Delete #{num} - {log.call}? (y/n): ").lower() == 'y':
                            del logs[i]
                            print(";) Deleted.")
                        break
                else:
                    print("Not found.")
            except:
                print("Invalid.")
            input("Press Enter to continue...")
        elif selection == 4:
            save_logs(logs, filename)
        elif selection == 5:  # Load Log Book
            clear_screen()
            print("=== Load Log Book File ===")
            txt_files = [f for f in os.listdir(".") if f.lower().endswith(".txt")]
            
            if txt_files:
                print("Available log files:")
                for i, f in enumerate(txt_files, 1):
                    print(f"  {i}. {f}")
                print("  0. Enter filename manually")
                
                try:
                    sel = int(input("\nEnter number: "))
                    if sel == 0:
                        new_filename = input("Enter filename: ").strip()
                    else:
                        new_filename = txt_files[sel-1]
                except:
                    new_filename = input("Enter filename: ").strip()
            else:
                new_filename = input("No .txt files found. Enter filename: ").strip()
            
            if not new_filename.endswith(".txt"):
                new_filename += ".txt"
            
            if new_filename != filename:
                if input(f"Load {new_filename}? (current unsaved changes will be lost) (y/n): ").lower() == 'y':
                    filename = new_filename
                    logs, next_number = load_logs(filename)
                    event = filename[:-4] if filename != "contacts.txt" else ""
            else:
                print("Already on this log file.")
                input("Press Enter to continue...")
        elif selection == 6:  # New Log Book
            if input("Start a completely new log book? (y/n): ").lower() == 'y':
                clear_screen()
                event = input("New Event Name: ").strip()
                filename = get_log_filename(event)
                logs = []
                next_number = 1
                print(f" New log started: {filename}")
                input("Press Enter...")
        elif selection == 7:
            if logs and input("Save before exit? (y/n): ").lower() == 'y':
                save_logs(logs, filename)
            print("73! Have a nice day, K4DZX!")
            break


if __name__ == "__main__":
    main()


    