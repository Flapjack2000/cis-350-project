from checklist import Checklist

def example_checklist_loop(days: int = 10) -> None:
    cl = Checklist(["Tiger", "Monkey", "Lions", "Zebra", "Fish", "Rattlesnake", "Meerkats"])

    for _ in range(days):
        print(f"Day {cl.day_count} - {'Day' if cl.is_day else 'Night'}: {list(cl.tasks.keys())}")
        for t in list(cl.tasks.keys()):
            cl.complete_task(t)

        print(f"Day {cl.day_count} - {'Day' if cl.is_day else 'Night'}: {list(cl.tasks.keys())}")
        for t in list(cl.tasks.keys()):
            cl.complete_task(t)

if __name__ == '__main__':
    example_checklist_loop()
