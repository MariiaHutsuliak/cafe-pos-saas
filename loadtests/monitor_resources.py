"""Моніторинг ресурсів сервера під час навантажувального тесту.

Кожні N секунд пише в CSV:
  - CPU і RAM процесу uvicorn (разом з дочірніми процесами);
  - CPU і RAM процесів PostgreSQL;
  - завантаження CPU і RAM всієї машини.

CPU процесів у відсотках одного ядра (200 означає два ядра на повну).

Запуск (приклад):
  python loadtests/monitor_resources.py --out results/resources_u50.csv

Зупинка: Ctrl+C або --duration. В кінці друкує середні й максимальні значення.
"""

import argparse
import csv
import time
from pathlib import Path

import psutil


def find_server_procs(match):
    """Процеси uvicorn і всі їхні діти (з --reload там два процеси)."""
    found = {}
    for proc in psutil.process_iter(["pid", "cmdline"]):
        cmdline = " ".join(proc.info["cmdline"] or [])
        if "uvicorn" in cmdline and match in cmdline:
            found[proc.pid] = proc
            try:
                for child in proc.children(recursive=True):
                    found[child.pid] = child
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    return found


def find_db_procs(name):
    found = {}
    for proc in psutil.process_iter(["pid", "name"]):
        if (proc.info["name"] or "").lower().startswith(name):
            found[proc.pid] = proc
    return found


def measure(procs, cache):
    """Сума CPU (%) і RSS (МБ) по групі процесів.

    cache тримає об'єкти Process між вимірами: cpu_percent рахується
    від попереднього виклику, тому об'єкти не можна створювати щоразу заново.
    """
    cpu_total = 0.0
    rss_total = 0
    for pid, proc in procs.items():
        proc = cache.setdefault(pid, proc)
        try:
            cpu_total += proc.cpu_percent(interval=None)
            rss_total += proc.memory_info().rss
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            cache.pop(pid, None)
    return cpu_total, rss_total / (1024 * 1024)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="results/resources.csv")
    parser.add_argument("--interval", type=float, default=1.0, help="секунди")
    parser.add_argument("--duration", type=float, default=0, help="0 = до Ctrl+C")
    parser.add_argument("--match", default="cafe_pos.main:app")
    parser.add_argument("--db-name", default="postgres")
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    server_cache = {}
    db_cache = {}
    psutil.cpu_percent(interval=None)  # перший виклик "заводить" лічильник

    rows = []
    start = time.time()
    print(f"Пишу в {out_path}. Зупинка: Ctrl+C")

    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "elapsed_s",
                "server_cpu_pct",
                "server_ram_mb",
                "db_cpu_pct",
                "db_ram_mb",
                "system_cpu_pct",
                "system_ram_pct",
            ]
        )
        # Перший вимір одразу, щоб прогріти cpu_percent у процесів.
        measure(find_server_procs(args.match), server_cache)
        measure(find_db_procs(args.db_name), db_cache)

        try:
            while True:
                time.sleep(args.interval)
                elapsed = time.time() - start
                s_cpu, s_ram = measure(find_server_procs(args.match), server_cache)
                d_cpu, d_ram = measure(find_db_procs(args.db_name), db_cache)
                row = [
                    round(elapsed, 1),
                    round(s_cpu, 1),
                    round(s_ram, 1),
                    round(d_cpu, 1),
                    round(d_ram, 1),
                    psutil.cpu_percent(interval=None),
                    psutil.virtual_memory().percent,
                ]
                writer.writerow(row)
                f.flush()
                rows.append(row)
                if args.duration and elapsed >= args.duration:
                    break
        except KeyboardInterrupt:
            pass

    if not rows:
        print("Жодного виміру не записано.")
        return
    if all(r[2] == 0 for r in rows):
        print(
            "Увага: процес uvicorn не знайдено. Перевір --match і що сервер запущений."
        )

    def avg(i):
        return sum(r[i] for r in rows) / len(rows)

    def peak(i):
        return max(r[i] for r in rows)

    print("\nПідсумок (середнє / максимум):")
    print(f"  сервер CPU, %      {avg(1):7.1f} / {peak(1):7.1f}")
    print(f"  сервер RAM, МБ     {avg(2):7.1f} / {peak(2):7.1f}")
    print(f"  PostgreSQL CPU, %  {avg(3):7.1f} / {peak(3):7.1f}")
    print(f"  PostgreSQL RAM, МБ {avg(4):7.1f} / {peak(4):7.1f}")
    print(f"  вся машина CPU, %  {avg(5):7.1f} / {peak(5):7.1f}")
    print(f"  вся машина RAM, %  {avg(6):7.1f} / {peak(6):7.1f}")


if __name__ == "__main__":
    main()
