import math
import os
import secrets
import string


os.system("")

LOWER = string.ascii_lowercase
UPPER = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = string.punctuation

MIN_LENGTH = 6
MAX_LENGTH = 128
MAX_COUNT = 100

COMMON_PASSWORDS = {
    "password", "parool", "123456", "12345678", "123456789", "qwerty",
    "qwerty123", "abc123", "111111", "000000", "iloveyou", "admin",
    "welcome", "letmein", "monkey", "dragon", "football", "master",
    "login", "passw0rd", "parool123", "salasona", "tere", "eesti",
}

LEVELS = [
    (30, "Väga nõrk"),
    (50, "Nõrk"),
    (70, "Keskmine"),
    (85, "Tugev"),
    (101, "Väga tugev"),
]


RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
PURPLE = "\033[35m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"

LEVEL_COLORS = {
    "Väga nõrk": RED,
    "Nõrk": RED,
    "Keskmine": YELLOW,
    "Tugev": GREEN,
    "Väga tugev": GREEN,
}

WIDTH = 60


def generate_password(length: int = 16, use_upper: bool = True,
                      use_digits: bool = True, use_symbols: bool = True) -> str:
    if not MIN_LENGTH <= length <= MAX_LENGTH:
        raise ValueError(
            f"Pikkus peab olema vahemikus {MIN_LENGTH}-{MAX_LENGTH}."
        )

    pools = [LOWER]
    if use_upper:
        pools.append(UPPER)
    if use_digits:
        pools.append(DIGITS)
    if use_symbols:
        pools.append(SYMBOLS)

    chars = [secrets.choice(pool) for pool in pools]

    all_chars = "".join(pools)
    chars += [secrets.choice(all_chars) for _ in range(length - len(chars))]

    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def character_classes(password: str) -> dict[str, bool]:
    return {
        "väiketähed": any(c in LOWER for c in password),
        "suurtähed": any(c in UPPER for c in password),
        "numbrid": any(c in DIGITS for c in password),
        "sümbolid": any(c in SYMBOLS for c in password),
    }


def calculate_entropy(password: str) -> float:
    if not password:
        return 0.0
    classes = character_classes(password)
    pool_size = 0
    if classes["väiketähed"]:
        pool_size += len(LOWER)
    if classes["suurtähed"]:
        pool_size += len(UPPER)
    if classes["numbrid"]:
        pool_size += len(DIGITS)
    if classes["sümbolid"]:
        pool_size += len(SYMBOLS)
    if pool_size == 0:
        pool_size = 32
    return len(password) * math.log2(pool_size)


def has_sequence(password: str) -> bool:
    text = password.lower()
    for i in range(len(text) - 2):
        a, b, c = ord(text[i]), ord(text[i + 1]), ord(text[i + 2])
        if b - a == c - b and abs(b - a) == 1:
            return True
    return False


def has_repeats(password: str) -> bool:
    return any(
        password[i] == password[i + 1] == password[i + 2]
        for i in range(len(password) - 2)
    )


def get_level(score: int) -> str:
    for limit, name in LEVELS:
        if score < limit:
            return name
    return LEVELS[-1][1]


FULL_SCORE_BITS = 90

PATTERN_PENALTY_BITS = 10

PATTERN_IGNORE_BITS = 100


def check_strength(password: str) -> dict:
    feedback = []

    if not password:
        return {"score": 0, "level": get_level(0), "entropy": 0.0,
                "feedback": ["Parool on tühi."]}

    entropy = calculate_entropy(password)


    distinct = len(set(password))
    effective = entropy * min(len(password), 2 * distinct) / len(password)


    if entropy < PATTERN_IGNORE_BITS:
        if has_sequence(password):
            effective -= PATTERN_PENALTY_BITS
            feedback.append("Väldi järjestikuseid märke (nt abc või 123).")
        if has_repeats(password):
            effective -= PATTERN_PENALTY_BITS
            feedback.append("Väldi sama märgi kordamist (nt aaa).")

    score = max(0, min(100, round(effective / FULL_SCORE_BITS * 100)))

    if len(password) < 12:
        feedback.append("Kasuta vähemalt 12 märki.")


    if score < 85:
        for name, present in character_classes(password).items():
            if not present:
                feedback.append(f"Lisa {name}.")

    if password.lower() in COMMON_PASSWORDS:
        score = min(score, 5)
        feedback.insert(0, "See on väga levinud parool, mida ei tohi kasutada!")

    if not feedback:
        feedback.append("Väga hea parool, jätka samas vaimus!")

    return {
        "score": score,
        "level": get_level(score),
        "entropy": entropy,
        "feedback": feedback,
    }


def paint(text: str, *styles: str) -> str:
    return "".join(styles) + text + RESET


def rule(char: str = "─") -> str:
    return paint(char * WIDTH, PURPLE)


def section(title: str) -> None:
    print()
    print(paint(title.upper(), BOLD, PURPLE))
    print(rule())


def info(text: str) -> None:
    print(paint(text, DIM))


def prompt(text: str) -> str:
    return input(paint(">>> ", PURPLE) + text)


def field(label: str, value: str, width: int = 12) -> None:
    print(f"{paint(label.ljust(width), PURPLE)}{value}")


def entropy_comment(bits: float) -> str:
    if bits < 28:
        return "Murtakse sekunditega."
    if bits < 36:
        return "Murtakse minutitega."
    if bits < 60:
        return "Võib olla murtav tundide või päevadega."
    if bits < 80:
        return "Päris kindel, aga tõsise ründaja vastu mitte väga."
    return "Praktiliselt murdmatu."


def banner() -> None:
    inner = WIDTH - 2
    print()
    print(paint("╔" + "═" * inner + "╗", PURPLE))
    print(paint("║", PURPLE) + " " * inner + paint("║", PURPLE))
    print(paint("║", PURPLE)
          + paint("PAROOLIGENERAATOR JA -KONTROLLIJA".center(inner), BOLD)
          + paint("║", PURPLE))
    print(paint("║", PURPLE) + " " * inner + paint("║", PURPLE))
    print(paint("╚" + "═" * inner + "╝", PURPLE))
    info("Loo turvalisi paroole ja kontrolli, kui tugev sinu oma on.")


def ask_yes_no(question: str, default: bool = True) -> bool:
    hint = "J/e" if default else "j/E"
    while True:
        answer = prompt(f"{question} ({hint}): ").strip().lower()
        if not answer:
            return default
        if answer in ("j", "jah", "y", "yes"):
            return True
        if answer in ("e", "ei", "n", "no"):
            return False
        print(paint("Palun vasta 'j' või 'e'.", YELLOW))


def ask_length(default: int = 16) -> int:
    while True:
        text = prompt(
            f"Parooli pikkus ({MIN_LENGTH}-{MAX_LENGTH}) [{default}]: "
        ).strip()
        if not text:
            return default
        try:
            length = int(text)
        except ValueError:
            print(paint("Palun sisesta täisarv.", YELLOW))
            continue
        if MIN_LENGTH <= length <= MAX_LENGTH:
            return length
        print(paint(f"Pikkus peab olema {MIN_LENGTH}-{MAX_LENGTH}.", YELLOW))


def generate_menu() -> None:
    section("Parooli genereerimine")
    info("Vasta küsimustele, Enter valib vaikeväärtuse.")
    print()
    length = ask_length()
    use_upper = ask_yes_no("Kas kasutada suurtähti?")
    use_digits = ask_yes_no("Kas kasutada numbreid?")
    use_symbols = ask_yes_no("Kas kasutada sümboleid?")

    count_text = prompt(f"Mitu parooli genereerida? (max {MAX_COUNT}) [1]: ").strip()
    count = int(count_text) if count_text.isdigit() and int(count_text) > 0 else 1
    count = min(count, MAX_COUNT)

    print()
    print(paint(f"Genereeritud paroolid ({count})", BOLD, PURPLE))
    print(rule())
    for number in range(1, count + 1):
        password = generate_password(length, use_upper, use_digits, use_symbols)
        result = check_strength(password)
        color = LEVEL_COLORS[result["level"]]
        print(f"{paint(str(number).rjust(3) + '.', DIM)} "
              f"{paint(password, BOLD)}  "
              f"{paint(result['level'], color)}"
              f"{paint(f'  {result['entropy']:.0f} bitti', DIM)}")
    print(rule())
    info("Salvesta parool paroolihaldurisse, ära saada seda e-postiga.")


def check_menu() -> None:
    section("Parooli kontrollimine")
    info("Sisesta parool ja saad teada, kui tugev see on ning kuidas seda parandada.")
    info("Parooli ei salvestata.")
    print()
    password = prompt("Sisesta kontrollitav parool: ")
    result = check_strength(password)
    color = LEVEL_COLORS[result["level"]]

    print()
    print(rule())
    field("Staatus", paint(f"{result['level']} ({result['score']}/100)", BOLD, color))
    field("Pikkus", f"{len(password)} märki")
    field("Entroopia", f"{result['entropy']:.1f} bitti")
    field("Hinnang", entropy_comment(result["entropy"]))

    print()
    print(paint("Märgiliigid", BOLD, PURPLE))
    for name, present in character_classes(password).items():
        print(f"  {name.ljust(12)}{'olemas' if present else paint('puudub', DIM)}")

    print()
    print(paint("Nõuanded", BOLD, PURPLE))
    for tip in result["feedback"]:
        print(f"  - {tip}")
    print(rule())


def tips_menu() -> None:
    section("Nipid turvaliste paroolide jaoks")
    tips = [
        ("Pikkus loeb", "Iga lisamärk teeb murdmise palju raskemaks. Sihi 12+ märki."),
        ("Kasuta segu", "Väike- ja suurtähed, numbrid ning sümbolid."),
        ("Väldi mustreid", "abc, 123, aaa ja qwerty proovitakse esimesena."),
        ("Ära korda", "Igale kontole oma parool, siis ühe lekke korral pole kõik ohus."),
        ("Väldi isiklikku infot", "Nimi, sünnipäev ja lemmikloom on kergesti äraarvatavad."),
        ("Kasuta paroolihaldurit", "Sa ei pea paljusid paroole ise meeles pidama."),
        ("Lülita sisse 2FA", "Kaheastmeline autentimine kaitseb ka lekkinud parooli korral."),
    ]
    for number, (head, body) in enumerate(tips, start=1):
        print(f"{paint(str(number) + '.', PURPLE)} {paint(head, BOLD)}")
        print(f"   {paint(body, DIM)}")
    print()
    print(rule())
    print(paint("Mis on entroopia?", BOLD, PURPLE))
    info("Mõõt bittides, kui ettearvamatu parool on.")
    info("Mida rohkem bitte, seda kauem võtab parooli murdmine aega.")
    print(rule())


def format_duration(seconds: float) -> str:
    if seconds < 1:
        return "alla sekundi"
    if seconds < 60:
        return f"{seconds:.0f} sekundit"
    if seconds < 3600:
        return f"{seconds / 60:.0f} minutit"
    if seconds < 86400:
        return f"{seconds / 3600:.0f} tundi"
    if seconds < 31_536_000:
        return f"{seconds / 86400:.0f} päeva"
    years = seconds / 31_536_000
    if years < 1_000_000_000:
        return f"{years:,.0f} aastat".replace(",", " ")
    return "miljardeid aastaid"


def crack_time_menu() -> None:
    section("Murdmisaja hinnang")
    info("Hindab, kui kaua võtaks parooli äraarvamine sõnastikuta jõumeetodil.")
    info("Arvestatakse keskmist aega, see on pool kõigist võimalikest variantidest.")
    print()
    password = prompt("Sisesta parool: ")
    if not password:
        print(paint("Parool on tühi.", YELLOW))
        return

    bits = calculate_entropy(password)
    attempts = 2 ** (bits - 1)
    scenarios = [
        ("Veebisisselogimine", "1 000 katset/s", 1_000),
        ("Kiire võrguväline rünnak", "10 miljardit katset/s", 10_000_000_000),
    ]

    print()
    print(rule())
    field("Pikkus", f"{len(password)} märki", 14)
    field("Entroopia", f"{bits:.1f} bitti", 14)
    print()
    for name, speed, rate in scenarios:
        if password.lower() in COMMON_PASSWORDS:
            duration = "kohe (levinud parool)"
        else:
            duration = format_duration(attempts / rate)
        print(paint(name, BOLD, PURPLE) + paint(f"  ({speed})", DIM))
        print(f"  {duration}")
    print(rule())
    info("Hinnang on optimistlik: ennustatavad mustrid murtakse tegelikult kiiremini.")


def main() -> None:
    banner()
    while True:
        section("Menüü")
        print(f"{paint('1', PURPLE)}  Genereeri parool")
        print(f"{paint('2', PURPLE)}  Kontrolli parooli tugevust")
        print(f"{paint('3', PURPLE)}  Nipid")
        print(f"{paint('4', PURPLE)}  Murdmisaja hinnang")
        print(f"{paint('5', PURPLE)}  Välju")
        print(rule())
        choice = prompt("Vali tegevus: ").strip()

        if choice == "1":
            generate_menu()
        elif choice == "2":
            check_menu()
        elif choice == "3":
            tips_menu()
        elif choice == "4":
            crack_time_menu()
        elif choice == "5":
            print(paint("\nNägemist!", PURPLE))
            break
        else:
            print(paint("Tundmatu valik, proovi uuesti.", YELLOW))


if __name__ == "__main__":
    main()
