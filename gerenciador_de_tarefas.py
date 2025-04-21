import flet as ft
import sqlite3
class ToDo:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.bgcolor = ft.Colors.BLUE_900
        self.page.window.width = 350
        self.page.window.height = 450
        self.page.window_resizable = False #tamanho da tela fixa
        self.page.window_always_on_top = True # a tela do aplicativo sempre ficará por cima
        self.page.title = 'Gerenciador de Taréfas'
        self.tasks = ''
        self.view = 'all'
        self.db_execute('CREATE TABLE IF NOT EXISTS tasks(nome, status)')
        self.results = self.db_execute("SELECT * FROM tasks")
        self.main_page()

    def db_execute(self, query, params=[]):
        with sqlite3.connect("database.db") as con:
            cursor = con.cursor()
            cursor.execute(query, params)
            con.commit()
            return cursor.fetchall()
        
    def checked(self, e):
        checked = e.control.value
        label = e.control.label

        if checked:
            self.db_execute('UPDATE tasks SET status = "complete" WHERE nome = ?', params=[label])
        else:
            self.db_execute('UPDATE tasks SET status = "incomplete" WHERE nome = ?', params=[label])

        if self.view == 'all':
            self.results = self.db_execute("SELECT * FROM tasks")
        else:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = ?', params=[self.view]) 

        self.update_task_list()
    def tasks_container(self):
        return ft.Container(
            height= self.page.height * 0.8,
            content=ft.Column(
                controls=[
                    ft.Checkbox(label= item[0], on_change=self.checked, value = True if item[1] =="complete" else "incomplete")
                    for item in self.results if item                        
                ]
            )
        )
    
    def set_task(self, e):
        self.tasks = e.control.value
        print(self.tasks)

    def add(self, e, input_task):
        name = self.tasks
        status="incomplete"

        if name:
            self.db_execute(query="INSERT INTO tasks VALUES (?, ?)", params=[name, status])
            input_task.value=''
            self.results = self.db_execute("SELECT * FROM tasks")
            self.update_task_list()
    
    def update_task_list(self):
        tasks=self.tasks_container()
        self.page.controls.pop()
        self.page.add(tasks)
        self.page.update()

    def select_tab(self, e):
        if e.control.selected_index ==0:
            self.results = self.db_execute("SELECT * FROM tasks ")
            self.view='all'
        elif e.control.selected_index ==1:
            self.results = self.db_execute("SELECT * FROM tasks WHERE status = 'incomplete'")
            self.view='incomplete'
        elif e.control.selected_index==2:
            self.results = self.db_execute(
                "SELECT * FROM tasks WHERE status = 'complete'")
            self.view='complete'
        
        self.update_task_list()
    def main_page(self):
       input_text = ft.TextField(hint_text='Digite a sua taréfa', expand=True, on_change=self.set_task)

       input_row = ft.Row(
           controls=[
               input_text,
               ft.FloatingActionButton(
                   icon = ft.Icons.ADD,
                   on_click=lambda e: self.add(e, input_task=input_text))
           ]
       )

       tabs = ft.Tabs(
           selected_index=0,
           tabs=[
               ft.Tab(text="Todos"),
               ft.Tab(text="Em andamento"),
               ft.Tab(text="Finalizados")
           ],
           animation_duration= 300,
           label_color= ft.Colors.AMBER,
           on_change=self.select_tab
       )

       task_container = self.tasks_container()
       self.page.add(input_row, tabs, task_container)


ft.app(target=ToDo)