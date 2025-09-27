from .keypad import Keypad
import time

# --- MAPPING  ---
ROWS = 4
COLS = 4
KEYS = [
    '1','2','3','A',
    '4','5','6','B',
    '7','8','9','C',
    '*','0','#','D'
]
rowsPins = [18, 23, 24, 25]
colsPins = [10, 22, 27, 17]   # změň 10 -> 5 pokud máš aktivní SPI

# --- NASTAVENÍ “BANKOMATU” ---
PIN_KOD = "1234"            # demo PIN (změň si)
MAX_POKUSU = 3
LOCKOUT_S = 10              # po 3 špatných pokusech pauza
PIN_MAX_LEN = 6             # povolená délka PINu

# --- POMOCNÉ FUNKCE ---
def wait_key(kp, timeout=None):
    """Blokující načtení 1 klávesy s volitelným timeoutem (v sekundách)."""
    start = time.time()
    while True:
        k = kp.getKey()
        if k != kp.NULL:
            return k
        if timeout is not None and (time.time() - start) > timeout:
            return None
        time.sleep(0.01)

def read_pin(kp, prompt="Zadej PIN:", max_len=PIN_MAX_LEN, timeout=20):
    """Čtení PINu s maskováním: číslice; A=Enter, B=Backspace, *=Clear, C=Cancel."""
    buffer = []
    print(prompt, end=" ", flush=True)
    print("")  # nový řádek
    while True:
        key = wait_key(kp, timeout=timeout)
        if key is None:
            print("\n⏱️ Timeout.")
            return None
        if key in "0123456789":
            if len(buffer) < max_len:
                buffer.append(key)
                print("\r" + "PIN: " + "*" * len(buffer) + " " * (max_len - len(buffer)), end="", flush=True)
        elif key == 'B':  # backspace
            if buffer:
                buffer.pop()
                print("\r" + "PIN: " + "*" * len(buffer) + " " * (max_len - len(buffer)), end="", flush=True)
        elif key == '*':  # clear
            buffer = []
            print("\r" + "PIN: " + "*" * 0 + " " * max_len, end="", flush=True)
        elif key == 'C':  # cancel
            print("\n❌ Zrušeno.")
            return None
        elif key == 'A':  # enter
            pin = "".join(buffer)
            print("\n")  # odřádkování
            return pin
        # ostatní klávesy ignoruj

def show_menu():
    print("\n=== MENU ===")
    print("1) Zůstatek")
    print("2) Vybrat 100 Kč")
    print("3) Vložit 100 Kč")
    print("D) Odhlásit")
    print("C) Zpět/Zrušit")
    print("Zvol možnost…")

def read_menu_choice(kp, timeout=30):
    while True:
        key = wait_key(kp, timeout=timeout)
        if key is None:
            print("⏱️ Timeout v menu.")
            return None
        if key in ('1','2','3','D','C'):
            return key
        # ignoruj ostatní

def main():
    print("Program startuje…")
    keypad = Keypad.Keypad(KEYS, rowsPins, colsPins, ROWS, COLS)
    keypad.setDebounceTime(50)  # ms

    # Demo účet
    balance = 1000
    pokusy = 0

    while True:
        pin = read_pin(keypad, "Zadej PIN:")
        if pin is None:
            # cancel/timeout => zpět na začátek
            continue
        if pin == PIN_KOD:
            print("✅ PIN OK. Vítej!")
            pokusy = 0
            # MENU LOOP
            while True:
                show_menu()
                choice = read_menu_choice(keypad)
                if choice is None:
                    print("Návrat na přihlášení…")
                    break
                if choice == '1':
                    print(f"💰 Zůstatek: {balance} Kč")
                elif choice == '2':
                    if balance >= 100:
                        balance -= 100
                        print("💸 Vybráno 100 Kč.")
                    else:
                        print("⚠️ Nedostatečný zůstatek.")
                elif choice == '3':
                    balance += 100
                    print("💵 Vloženo 100 Kč.")
                elif choice == 'C':
                    print("↩️ Zpět.")
                    # jen překresli menu
                elif choice == 'D':
                    print("👋 Odhlášení.")
                    break
                time.sleep(0.5)
        else:
            pokusy += 1
            zbyva = MAX_POKUSU - pokusy
            if zbyva > 0:
                print(f"❌ Špatný PIN. Zbývá pokusů: {zbyva}.")
            if pokusy >= MAX_POKUSU:
                print


