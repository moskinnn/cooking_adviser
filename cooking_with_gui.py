"""
Программа для поиска идей в приготовлении блюд из имеющихся в холодильнике продуктов.

В первом поле рабочего окна пользователь вводит названия продуктов, которые хочет использовать в готовке.
Далее из базы данных выбираются рецепты, содержащие указанные продукты. Пользователю предлагаются несколько из них.
Выбрав понравившееся блюдо, пользователь получает полный список ингредиентов и инструкцию по приготовлению.
При желании рецепт можно записать в .txt файл и открыть его в Блокноте.
"""

import os
import pandas as pd
import sqlite3 as sq
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from PIL import ImageTk
from ast import literal_eval
from tabulate import tabulate


class Gui:
    """Основное окно программы"""

    def __init__(self):
        self.root = Tk()
        self.root.title("cooking_gui")
        self.root.geometry("667x800")
        self.root.resizable(False, False)

        self.foodstuff = None
        self.query_results = None
        self.five_results = None
        self.choice = None
        self.img = None
        self.selected_dish = None
        self.all_ingredients = None
        self.how_to_make = None

        self.lbl_ask1 = Label(self.root, text="Какие продукты вы хотите использовать?")
        self.lbl_ask1.grid(row=0, column=0, columnspan=7, stick='w')

        self.lbl_write_it = Label(self.root, text="Перечислите через запятую: ")
        self.lbl_write_it.grid(row=1, column=0, columnspan=2, stick='w')

        self.ent_input = Entry(self.root)
        self.ent_input.grid(row=1, column=2, columnspan=4, stick='we')

        self.btn_conf1 = Button(self.root, text="Подтвердить", command=self.get_dishes)
        self.btn_conf1.grid(row=1, column=6)

        self.lbl_use_for = Label(self.root, text="Здесь будут предложены несколько блюд на выбор:")
        self.lbl_use_for.grid(row=2, column=0, columnspan=7, pady=(8, 0), stick='w')

        self.txt_for_choice = Text(self.root, width=82, height=7, wrap=NONE)
        self.txt_for_choice.grid(row=3, column=0, columnspan=7, padx=3, stick='w')

        self.lbl_ask2 = Label(self.root, text="Какое блюдо вы хотите приготовить?")
        self.lbl_ask2.grid(row=4, column=0, columnspan=7, pady=(8, 0), stick='w')

        self.lbl_choice_is = Label(self.root, text="Вы выбрали:")
        self.lbl_choice_is.grid(row=6, column=0, columnspan=2, stick='w')

        self.ent_title = Entry(self.root)
        self.ent_title.grid(row=6, column=1, columnspan=5, stick='we')

        self.btn_choice1 = Button(self.root, text="1", command=lambda: self.get_choice(1))
        self.btn_choice1.grid(row=5, column=1, stick='we')

        self.btn_choice2 = Button(self.root, text="2", command=lambda: self.get_choice(2))
        self.btn_choice2.grid(row=5, column=2, stick='we')

        self.btn_choice3 = Button(self.root, text="3", command=lambda: self.get_choice(3))
        self.btn_choice3.grid(row=5, column=3, stick='we')

        self.btn_choice4 = Button(self.root, text="4", command=lambda: self.get_choice(4))
        self.btn_choice4.grid(row=5, column=4, stick='we')

        self.btn_choice5 = Button(self.root, text="5", command=lambda: self.get_choice(5))
        self.btn_choice5.grid(row=5, column=5, stick='we')

        self.btn_another = Button(self.root, text="Другой набор\nблюд", command=self.get_five_results)
        self.btn_another.grid(row=5, column=6, rowspan=2)

        self.lbl_image = Label(self.root, text="Изображение\nблюда", height=10)
        self.lbl_image.grid(row=7, column=1, columnspan=3, stick='we')

        self.btn_conf2 = Button(self.root, text="Подтвердить", height=3, command=self.get_recipe)
        self.btn_conf2.grid(row=7, column=4, columnspan=2)

        self.lbl_here_is1 = Label(self.root, text="Полный список ингредиентов:")
        self.lbl_here_is1.grid(row=8, column=0, columnspan=3, pady=(8, 0), stick='w')

        self.txt_full_ingr = ScrolledText(self.root, height=8, wrap=WORD)
        self.txt_full_ingr.grid(row=9, column=0, columnspan=7, padx=3, stick='we')

        self.lbl_here_is2 = Label(self.root, text="Инструкция по приготовлению:")
        self.lbl_here_is2.grid(row=10, column=0, columnspan=4, pady=(8, 0), stick='w')

        self.txt_full_instr = ScrolledText(self.root, height=8, width=40, wrap=WORD)
        self.txt_full_instr.grid(row=11, column=0, columnspan=7, padx=3, stick='we')

        self.btn_to_file = Button(self.root, text="Записать рецепт в файл", height=2,
                                  command=lambda: self.to_file(self.foodstuff, self.all_ingredients, self.how_to_make))
        self.btn_to_file.grid(row=12, column=0, columnspan=2, padx=(6, 0), pady=(8, 0), stick='we')

        self.btn_open_file = Button()

        self.btn_exit = Button(self.root, text="Выход", height=2, command=self.close)
        self.btn_exit.grid(row=12, column=6, padx=(0, 5), pady=(8, 0), stick='we')

    def run(self):
        self.root.mainloop()

    def close(self):
        self.root.destroy()

    def get_dishes(self):
        """Возвращает DataFrame с выборкой из БД на основе списка ингредиентов"""
        self.foodstuff = self.ent_input.get().lower().split(", ")
        with sq.connect('cooking.db') as con:
            cur = con.cursor()
            cur.execute(f"""
            SELECT title, ingredients, instructions, image_name
            FROM dataset
            WHERE {" AND ".join(["ingredients LIKE '%" + ingredient + "%'" for ingredient in self.foodstuff])}
            """)
        self.query_results = pd.DataFrame(cur.fetchall(),
                                          columns=['название_блюда', 'ингредиенты', 'инструкция', 'изображение'])
        # очищаем и приводим данные в двух полях к спискам
        self.query_results['ингредиенты'] = self.query_results['ингредиенты'].apply(literal_eval)
        self.query_results['инструкция'] = self.query_results['инструкция'].apply(lambda x: list(x.split(". ")))
        self.get_five_results()

    def get_five_results(self):
        """Выбирает до пяти случайных рецептов из общего результата"""
        self.five_results = self.query_results.sample(n=min(5, len(self.query_results.index))).reset_index(drop=True)
        self.five_results.index = self.five_results.index + 1
        # запрашиваем краткое описание возможных блюд
        self.get_short_description(self.foodstuff, self.five_results)

    def get_short_description(self, stuff, five_results):
        """Выводит в текстовое поле DataFrame [позиция для выбора, название, продуктов в списке/всего по рецепту]"""
        five_results['в_наличии'] = [str(len(stuff)) + "/" + str(len(ingr)) for ingr in five_results['ингредиенты']]
        self.txt_for_choice.delete(1.0, END)
        self.txt_for_choice.insert(1.0, tabulate(five_results[['название_блюда', 'в_наличии']],
                                                 headers='keys',
                                                 tablefmt='presto',
                                                 stralign='left'))
        # указывается, сколько всего найдено рецептов с введенными продуктами
        self.lbl_use_for.config(text=f"Эти ингредиенты используются для приготовления {len(self.query_results.index)} блюд. Вот несколько из них:")

    def get_choice(self, number):
        """Выводит в текстовое поле название выбранного блюда и заменяет Label на изображение из папки"""
        self.choice = number
        self.selected_dish = self.five_results.loc[number, 'название_блюда']

        self.ent_title.delete(0, END)
        self.ent_title.insert(0, " "+self.selected_dish)

        self.img = ImageTk.PhotoImage(file=f"food_images\\{self.five_results.loc[number, 'изображение']}.jpg")
        self.lbl_image.config(height=152, image=self.img)

    def get_recipe(self):
        """Выводит в два текстовых поля список ингредиентов и рецепт выбранного блюда"""
        self.all_ingredients = self.five_results.loc[self.choice, 'ингредиенты']
        self.how_to_make = self.five_results.loc[self.choice, 'инструкция']

        self.txt_full_ingr.delete(1.0, END)
        self.txt_full_ingr.insert(1.0, "\n".join(self.all_ingredients))
        self.txt_full_instr.delete(1.0, END)
        self.txt_full_instr.insert(1.0, "\n".join(self.how_to_make))

    def to_file(self, input_list, ingredients, instruction):
        """Создает файл с введенным списком продуктов и рецептом выбранного блюда"""
        with open("recipe.txt", "w", encoding='utf-8') as file:
            file.write("Будем использовать следующие продукты:\n")
            file.write("\t" + ", ".join(input_list))
            file.write('\n\nВсе ингредиенты для "' + self.selected_dish + '":\n')
            file.writelines("\t" + ingredient + "\n" for ingredient in ingredients)
            file.write('\nРецепт:\n\n')
            file.writelines(step + "\n" for step in instruction)
        # создается кнопка открытия записанного файла
        self.btn_open_file = Button(self.root, text="Открыть файл", height=2, command=self.open_notepad)
        self.btn_open_file.grid(row=12, column=2, columnspan=2, padx=(5, 0), pady=(8, 0), stick="we")

    @staticmethod
    def open_notepad():
        """Открывает последнюю версию файла с рецептом"""
        os.system("notepad recipe.txt")


window = Gui()
window.run()
