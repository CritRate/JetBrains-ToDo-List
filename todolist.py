import sys

from sqlalchemy import create_engine, Column, Integer, String, Date, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta

Base = declarative_base(())

date_format = '%A %d %b'


class Table(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String, default='')
    deadline = Column(Date, default=datetime.today())

    def __repr__(self):
        d = self.deadline.strftime("%d %b").lstrip('0')
        return f'{self.task}. {d}'


def create_session():
    engine = create_engine('sqlite:///todo.db?check_same_thread=False')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def menu():
    options = [
        'Today\'s tasks',
        'Week\'s tasks',
        'All tasks',
        'Missed tasks',
        'Add task',
        'Delete task',
        'Exit'
    ]
    menu_str = ''.join([f'{i + 1}) {s}\n' if i != len(options) - 1 else f'0) {s}\n' for i, s in enumerate(options)])
    return input(menu_str)


class Todo:
    def __init__(self):
        self.session: Session = create_session()

    def add_task(self, task, deadline=None):
        if deadline is None:
            new_task = Table(task=task)
        else:
            new_task = Table(task=task, deadline=deadline)

        self.session.add(new_task)
        self.session.commit()
        return True

    def delete_task(self, task_id):
        self.session.query(Table).filter(Table.id == task_id).delete()
        self.session.commit()
        return True

    def get_all_tasks(self):
        return self.session.query(Table).order_by(Table.deadline).all()

    def get_today_task(self):
        return self.session.query(Table).filter(Table.deadline == datetime.today().date()).all()

    def get_week_task(self):
        return self.session.query(Table).filter(
            Table.deadline > datetime.today().date() - timedelta(days=7)).order_by(Table.deadline).all()

    def get_missed_tasks(self):
        return self.session.query(Table).filter(Table.deadline < datetime.today().date()).all()

    def print_tasks(self, tasks, week_formatting=False):
        task_ids = {}
        if tasks:
            for i, task in enumerate(tasks, start=1):
                if week_formatting:
                    print(f'{i} {task.task}')
                else:
                    print(f'{i}. {task}')
                task_ids[i] = task.id

            print()
        else:
            print('Nothing to do!\n')
        return task_ids

    def print_week_tasks(self):
        tasks = self.get_week_task()

        current_day = datetime.today().date()

        for i in range(7):
            print(current_day.strftime(date_format).replace(' 0', ' ') + ':')
            day_tasks = []
            for t in tasks:
                if current_day == t.deadline:
                    day_tasks.append(t)
            self.print_tasks(tasks=day_tasks, week_formatting=True)
            current_day += timedelta(days=1)


if __name__ == '__main__':
    todo = Todo()

    while True:
        option = menu()
        print()
        if option == '1':
            print(datetime.today().strftime(date_format).replace(' 0', ' ') + ':')
            todo.print_tasks(todo.get_today_task())
        if option == '2':
            todo.print_week_tasks()
        if option == '3':
            print('All tasks:')
            todo.print_tasks(todo.get_all_tasks())
            print()
        if option == '4':
            print('Missed tasks:')
            todo.print_tasks(todo.get_missed_tasks())
        if option == '5':
            text = input('Enter task\n')
            date = datetime.strptime(input('Enter deadline\n'), '%Y-%m-%d')
            success = todo.add_task(task=text, deadline=date)
            if success:
                print('The task has been added!\n')
        if option == '6':
            print('Choose the number of the task you want to delete:')
            task_ids = todo.print_tasks(todo.get_all_tasks())
            option = int(input())
            result = todo.delete_task(task_id=task_ids.get(option))
            if result:
                print('The task has been deleted!\n')
        if option == '0':
            print('Bye!')
            sys.exit()
