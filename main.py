import pyodbc
from PySimpleGUI import PySimpleGUI as sg
from PIL import Image
import io
import os
from datetime import date
from enum import Enum
from tkinter import filedialog
import shutil
from datetime import datetime

data = (
    "Driver={SQL Server};"
    "Server=TERMINAL\CDS;"
    "Database=Teste;"
)

connection = pyodbc.connect(data)
print("Successfully connected")

cursor = connection.cursor()

#query = """INSERT INTO Entradas(cliente, tipo, fabricante, id, data_entrada, data_saida, orcamento, imagens)
#VALUES
#        ('Tintepoxi', 'Queimador', 'Rielo', 'id-ruffles-feijuca', '20230815', '20230816', '01-Repimboca da parafuseta', 'nulas')
#"""

#cursor.execute(query)
#cursor.commit()

class states(Enum):
    MAIN = 0
    SEARCH = 1
    READ = 2
    WRITE = 3
    SEARCH_LIST = 4
    EDIT_ENTRY = 5

state = states.MAIN

row_counter = 0

image_files = []

storage_folder = 'C:\\Users\\Tintepoxi\\Desktop\\testecricao'

def array_to_data(array):
    im = Image.fromarray(array)
    with io.BytesIO() as output:
        im.save(output, format="PNG")
        data = output.getvalue()
    return data

def fetch_search_page_data():
    sdata = []
    sdata += [['desconhecido']+[item[0] for item in cursor.execute("SELECT DISTINCT cliente FROM Entradas_teste").fetchall()]]
    sdata += [['desconhecido']+[item[0] for item in cursor.execute("SELECT DISTINCT fabricante FROM Entradas_teste").fetchall()]]
    sdata += [['desconhecido']+[item[0] for item in cursor.execute("SELECT DISTINCT tipo FROM Entradas_teste").fetchall()]]
    sdata += [['desconhecido']+[item[0] for item in cursor.execute("SELECT DISTINCT YEAR(data_entrada) FROM Entradas_teste").fetchall()]]
    sdata += [['desconhecido']+[item[0] for item in cursor.execute("SELECT DISTINCT YEAR(data_saida) FROM Entradas_teste").fetchall()]]
    return sdata

def fetch_search_data(client, equip, fab, eid, arrive, depart):
    infos = [('cliente', client), ('tipo',equip), ('fabricante',fab), ('id',eid), ('data_entrada',arrive), ('data_saida',depart)]
    query = "SELECT * From Entradas_teste "

    start = False
    for info in infos:
        if info[1] != '' and info[1] != 'desconhecido':

            empty = False
            if type(info[1]) is tuple:
                empty = True
                for i in info[1]:
                    if i != '' and i != 'desconhecido':
                        empty = False

            if not start and not empty:
                start = True
                query += "WHERE "
            elif not empty:
                query += "AND "

            if 'data' in info[0]:

                year = False
                month = False

                if info[1][0] != '' and info[1][0] != 'desconhecido':
                    query += f"YEAR({info[0]}) = {info[1][0]} "
                    year = True

                if info[1][1] != 'desconhecido':
                    if year:
                        query += "AND "
                    query += f"MONTH({info[0]}) = {info[1][1]} "
                    month = True

                if info[1][2] != '' and info[1][2] != 'desconhecido':
                    if month:
                        query += "AND "
                    query += f"DAY({info[0]}) = {info[1][0]} "

                continue

            query += f"{info[0]} LIKE '{info[1]}' "

    print(query)
    sdata = cursor.execute(query).fetchall()
    result = []
    column_names = [column[0] for column in cursor.description]
    for row in sdata:
        result.append(dict(zip(column_names, row)))

    return result




def fetch_write_page_data():
    wdata = []
    wdata += [[item[0] for item in cursor.execute("SELECT DISTINCT cliente FROM Entradas_teste").fetchall()]]
    wdata += [[item[0] for item in cursor.execute("SELECT DISTINCT fabricante FROM Entradas_teste").fetchall()]]
    wdata += [[item[0] for item in cursor.execute("SELECT DISTINCT tipo FROM Entradas_teste").fetchall()]]
    return wdata

def fetch_read_page_data(rClient, rType, rArrive, rID):
    return cursor.execute(f"""SELECT orcamento, imagens From Entradas_teste WHERE id = '{rID}' AND data_entrada = '{rArrive}'
                            AND cliente = '{rClient}' AND tipo = '{rType}'""").fetchall()

def fetch_edit_page_data(rClient, rType, rArrive, rID):
    wdata = []
    wdata += [[item[0] for item in cursor.execute("SELECT DISTINCT cliente FROM Entradas_teste").fetchall()]]
    wdata += [[item[0] for item in cursor.execute("SELECT DISTINCT fabricante FROM Entradas_teste").fetchall()]]
    wdata += [[item[0] for item in cursor.execute("SELECT DISTINCT tipo FROM Entradas_teste").fetchall()]]


def create_row(path):
    global row_counter

    """image = Image.open(
        'C:/Users/Tintepoxi/Desktop/Clientes Manutenção Tintepoxi/2023/Madelar/4a2ea0e1-3585-498f-bb24-f1b1a482b8a5.jpeg')
    image.thumbnail((400, 400))
    bio = io.BytesIO()
    print(bio.__class__)
    image.save(bio, format="PNG")"""

    print(path)

    if not path or path == 'nulo' or path == 'nulas' or path == '':
        print("TAIGOOOOO")
        return [
            sg.pin(
                sg.Col([
                    [sg.Image(data=[], key=('-IMG-', -1))]
                ], key=f'-ROW-1-')
            )
        ]

    rows_to_add = []

    for file in os.listdir(path):
        #print(os.path.join(path,file))
        #img = cv2.imread(os.path.join(path,file), -1).tobytes()
        #print(cv2.imread(os.path.join(path,file), -1).tobytes().__class__)

        image = Image.open(os.path.join(path, file))
        image.thumbnail((400, 400))
        bio = io.BytesIO()
        image.save(bio, format="PNG")

        if image is not None:

            row = [
                sg.pin(
                    sg.Col([
                        [sg.Image(data=bio.getvalue(), key=('-IMG-', row_counter))]
                    ], key=f'-ROW{row_counter}-')
                )
            ]
            row_counter += 1
            rows_to_add.append(row)

    return rows_to_add

def create_main_window():
    sg.theme("Reddit")

    layout_main = [
        [sg.Text('Arrumador 3000', font='Helvetica 32 bold', expand_x=True, justification='center')],
        [sg.Button('Buscar no registo', font='Helvetica 16', key="-btRead-", size=(0, 3)),
         sg.Button('Adicionar ao registro', font='Helvetica 16', key="-btWrite-", size=(0, 3))]
    ]

    layout_write = [
        [sg.Text('Gravador 3000', font='Helvetica 32 bold', expand_x=True, justification='center')],
        [sg.Text('preencha com os dados de entrada', font=('Arial Baltic', 16), expand_x=True, justification='center', key='-WDisc-')],
        [sg.Text('Cliente:', font=('Arial Baltic', 12), size=(20,0), justification='left'),
         sg.Combo(values='', tooltip='Preencha com o nome do cliente', expand_x=True, key='-inpWClient-')],
        [sg.Text('Tipo do equipamento:', font=('Arial Baltic', 12), size=(20,0), justification='left'),
         sg.Combo('', expand_x=True, key='-inpWType-')],
        [sg.Text('Fabricante:', font=('Arial Baltic', 12), size=(20, 0), justification='left'),
         sg.Combo(values='', tooltip='Preencha com o nome do fabricante do equipamento', expand_x=True, key='-inpWFab-')],
        [sg.Text('Identificação:', font=('Arial Baltic', 12), size=(20, 0), justification='left'),
         sg.Input(tooltip='Preencha com o número de identificação do equipamento', expand_x=True, key='-inpWID-')],
        [sg.Text('Orçamento:', font=('Arial Baltic', 12), size=(20, 0), justification='left')],
         [sg.Multiline(tooltip='Preencha com os dados do orçamento',sbar_relief=sg.RELIEF_FLAT, expand_x=True, size=(0,8),key='-inpWBudget-')],
        [sg.Button('Anexar Imagens', font=('Arial Baltic', 12),size=(0,2), key='-btWImg'),
         sg.Multiline(expand_x=True, size=(0,3), disabled=True,sbar_relief=sg.RELIEF_FLAT, write_only=True,key='-imgArchivesTxt-')],
        [sg.Button('Cancelar', font=('Arial Baltic', 12), key='-btWCancel-'),
         sg.HSeparator(),
         sg.Button('Submeter', font=('Arial Baltic', 12), key='-btWSub-')]
    ]

    layout_search = [
        [sg.Text('Procuração 3000', font='Helvetica 32 bold', expand_x=True, justification='center')],
        [sg.Text('procure por entradas no Banco de Dados', font=('Arial Baltic', 16), expand_x=True, justification='center')],
        [sg.Text('Cliente:', font=('Arial Baltic', 12), size=(20, 0), justification='left'),
         sg.Combo('',tooltip='Preencha com o nome do cliente', expand_x=True, key='-inpSClient-')],
        [sg.Text('Tipo do equipamento:', font=('Arial Baltic', 12), size=(20, 0), justification='left'),
         sg.Combo('', expand_x=True, readonly=True, key='-inpSType-')],
        [sg.Text('Fabricante:', font=('Arial Baltic', 12), size=(20, 0), justification='left'),
         sg.Combo('', tooltip='Preencha com o nome do fabricante do equipamento', expand_x=True, key='-inpSFab-')],
        [sg.Text('Identificação:', font=('Arial Baltic', 12), size=(20, 0), justification='left'),
         sg.Input(tooltip='Preencha com o número de identificação do equipamento', expand_x=True, key='-inpSID-')],
        [sg.HorizontalSeparator()],
        [sg.Text('Ano, Mês e(ou) dia de entrada:', font=('Arial Baltic', 12), size=(20, 0), justification='left'),
         sg.Combo(['desconhecido'], default_value='desconhecido', expand_x=True, key='-inpSArriveYear-'),
         sg.Combo(['desconhecido', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], default_value='desconhecido', readonly=True,
                  expand_x=True, key='-inpSArriveMonth-'),
         sg.Input(default_text='desconhecido', size=(12, 0), key='-inpSArriveDay-')],
        [sg.HorizontalSeparator()],
        [sg.Text('Ano, Mês e(ou) dia de Saída:', font=('Arial Baltic', 12), size=(20, 0), justification='left'),
         sg.Combo(['desconhecido'], default_value='desconhecido', expand_x=True, key='-inpSDepartureYear-'),
         sg.Combo(['desconhecido', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], default_value='desconhecido', readonly=True,
                  expand_x=True, key='-inpSDepartureMonth-'),
         sg.Input(default_text='desconhecido', size=(12, 0), key='-inpSDepartureDay-')],

        [sg.Button('Cancelar', font=('Arial Baltic', 12), key='-btSCancel-'),
         sg.HSeparator(),
         sg.Button('Procurar', font=('Arial Baltic', 12), key='-btSSub-')]
    ]

    layout_search_list = [
        [sg.Text('Lista de resultados 3000', font='Helvetica 32 bold', expand_x=True, justification='center')],
        [sg.Text('Selecione um resultado da pesquisa para ver detalhes', font=('Arial Baltic', 16), expand_x=True,
                 justification='center')],
        [sg.Table(values=[], headings=['Cliente', 'Equipamento', 'Fabricante', 'Data de entrada', 'Data de saída', 'Identificação'], max_col_width=35, auto_size_columns=True, expand_x=True, justification='center',
                  num_rows=10, row_height=35, key='-results_table-')],
        [sg.Button('Voltar', font=('Arial Baltic', 12), key='-btSLBack-'), sg.HSeparator(),
                    sg.Button('Acessar', font=('Arial Baltic', 12), key='-btSLAccess-')]
    ]

    img_col = [sg.Frame('imagens:', layout=[[sg.Input('caminhos', readonly=True, expand_x=True, key='rd_InpImgPath')], [sg.Column([create_row('')], scrollable=True, vertical_scroll_only=True, expand_y=True, expand_x=True, key='-rd_img_frame-')]], size=(400,500))]

    layout_read = [
        [sg.Text('Leitura 3000', font='Helvetica 32 bold', expand_x=True, justification='center')],
        [sg.Column([
            [sg.Text('Dados do equipamento', font=('Arial Baltic', 16), expand_x=True,
                     justification='center')],
            [sg.Text('Cliente:'), sg.Text('Tintepoxi', key='rd_client')],
            [sg.Text('Equipamento:'), sg.Text('Fonte eletrostática', key='rd_equip')],
            [sg.Text('Fabricante:'), sg.Text('Adal-Tecno', key='rd_fab')],
            [sg.Text('Identificação:'), sg.Text('4002-8922', key='rd_id')],
            [sg.Text('Data de entrada:'), sg.Text('10/05/1844', key='rd_arrive_date')],
            [sg.Text('Data de saída:'), sg.Text('ainda na empresa', key='rd_depart_date')],
            [sg.HSeparator()],
            [sg.Text('Orçamento:')],
            [sg.Multiline('Serviço de manutenção\n01-Repimboca da parafuseta\n01-A peça\n01-Esquadro '
                          'redondo\n01-Martelo de desempenar vidro', horizontal_scroll=True, disabled=True, expand_x=True, size=(0,15), key='rd_budget')],
            [sg.Button('Voltar', font=('Arial Baltic', 12), key='-btRBack-'),
             sg.HSeparator(), sg.Button('Editar', font=('Arial Baltic', 12), key='-btREdit-')]
        ], vertical_alignment='top'),

            sg.Column([img_col], key='-rd_images-')],
    ]

    layout_edit = [
        [sg.Text('Editor 3000', font='Helvetica 32 bold', expand_x=True, justification='center')],
        [sg.Text('Modifique os dados de entrada', font=('Arial Baltic', 16), expand_x=True, justification='center', key='-EDisc-')],
        [sg.Text('Cliente:', font=('Arial Baltic', 12), size=(20,0), justification='left'),
         sg.Combo(values='', tooltip='Preencha com o nome do cliente', expand_x=True, key='-inpEClient-')],
        [sg.Text('Tipo do equipamento:', font=('Arial Baltic', 12), size=(20,0), justification='left'),
         sg.Combo('',expand_x=True, key='-inpEType-')],
        [sg.Text('Fabricante:', font=('Arial Baltic', 12), size=(20, 0), justification='left'),
         sg.Combo(values='', tooltip='Preencha com o nome do fabricante do equipamento', expand_x=True, key='-inpEFab-')],
        [sg.Text('Identificação:', font=('Arial Baltic', 12), size=(20, 0), justification='left'),
         sg.Input(tooltip='Preencha com o número de identificação do equipamento', expand_x=True, key='-inpEID-')],
        [sg.Text('Orçamento:', font=('Arial Baltic', 12), size=(20, 0), justification='left')],
         [sg.Multiline(tooltip='Preencha com os dados do orçamento',sbar_relief=sg.RELIEF_FLAT, expand_x=True, size=(0,8),key='-inpEBudget-')],
        [sg.Text('Data de chegada: ', size=(15,0), font=('Arial Baltic', 12), justification='left'),
         sg.InputText(default_text='', font=('Arial Baltic', 12), size=(9, 0), justification='left', key='-EArriveDate-'),
         sg.CalendarButton('Selecione uma data', close_when_date_chosen=True, target='-EArriveDate-', format='%d/%m/%Y', size=(20,1))],
        [sg.Text('Data de saída: ', size=(15,0), font=('Arial Baltic', 12), justification='left'),
         sg.InputText(default_text='', font=('Arial Baltic', 12), size=(9, 0), justification='left',
                      key='-EDepartureDate-'),
         sg.CalendarButton('Selecione uma data', close_when_date_chosen=True, target='-EDepartureDate-', format='%d/%m/%Y',
                           size=(20, 1))],
        [sg.Button('Cancelar', font=('Arial Baltic', 12), key='-btECancel-'),
         sg.HSeparator(),
         sg.Button('Modificar', font=('Arial Baltic', 12), key='-btESub-')]
    ]

    layout_geral = [[sg.Column(layout=layout_main, visible=True, key='-MAIN_PAGE-'),
                     sg.Column(layout=layout_search, visible=False, key='-SEARCH_PAGE-'),
                     sg.Column(layout=layout_read, visible=False, key='-READ_PAGE-'),
                     sg.Column(layout=layout_write, visible=False, key='-WRITE_PAGE-'),
                     sg.Column(layout=layout_search_list, visible=False, key='-SEARCH_LIST_PAGE-'),
                     sg.Column(layout=layout_edit, visible=False, key='-EDIT_PAGE-')]]

    window = sg.Window("Arrumador 3000", layout_geral, finalize=True, use_default_focus=False)

    global state
    global row_counter
    global image_files
    global storage_folder

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break

        if state == states.MAIN:
            # MAIN ###################################################
            if event == "-btRead-":
                print("ler")

                data = fetch_search_page_data()
                #print(data)

                window['-inpSClient-'].update(values=data[0])
                window['-inpSFab-'].update(values=data[1])
                window['-inpSType-'].update(values=data[2])
                window['-inpSArriveYear-'].update(values=data[3])
                window['-inpSDepartureYear-'].update(values=data[4])

                window['-MAIN_PAGE-'].update(visible=False)
                window['-SEARCH_PAGE-'].update(visible=True)

                state = states.SEARCH

            if event == "-btWrite-":
                data = fetch_write_page_data()

                window['-inpWClient-'].update(values=data[0])
                window['-inpWFab-'].update(values=data[1])
                window['-inpWType-'].update(values=data[2])

                window['-MAIN_PAGE-'].update(visible=False)
                window['-WRITE_PAGE-'].update(visible=True)

                state = states.WRITE
                print("adicionar")


        elif state == states.SEARCH:
            # SEARCH ###################################################
            """TODO:
                    preencher o combo box do cliente
                    preencer o combo box do fabricante
                    preencher o combo box dos anos de saída e entrada
            """
            if event == '-btSCancel-':
                window['-SEARCH_PAGE-'].update(visible=False)
                window['-MAIN_PAGE-'].update(visible=True)

                state = states.MAIN

            if event == '-btSSub-':
                search_data = fetch_search_data(values['-inpSClient-'], values['-inpSType-'], values['-inpSFab-'], values['-inpSID-'],
                                  (values['-inpSArriveYear-'], values['-inpSArriveMonth-'], values['-inpSArriveDay-']),
                                  (values['-inpSDepartureYear-'], values['-inpSDepartureMonth-'], values['-inpSDepartureDay-']))

                #print
                valores = []

                for data in search_data:
                    val = list(data.values())
                    del val[5:7]
                    valores.append(val)

                for row in valores:
                    row[3] = datetime.strptime(row[3], '%Y-%m-%d').date().strftime('%d/%m/%Y')
                    try:
                        row[4] = datetime.strptime(row[4], '%Y-%m-%d').date().strftime('%d/%m/%Y')
                    except:
                        row[4] = 'Ainda na Empresa'

                window['-results_table-'].update(values=valores)

                window['-SEARCH_PAGE-'].update(visible=False)
                window['-SEARCH_LIST_PAGE-'].update(visible=True)

                state = states.SEARCH_LIST

        elif state == states.SEARCH_LIST:
            if event == '-btSLBack-':
                window['-SEARCH_LIST_PAGE-'].update(visible=False)
                window['-SEARCH_PAGE-'].update(visible=True)

                state = states.SEARCH

            if event == '-btSLAccess-':
                if not len(values['-results_table-']):
                    continue
                selected = window['-results_table-'].get()[values['-results_table-'][0]]
                print(selected)

                window['rd_client'].update(selected[0])
                window['rd_equip'].update(selected[1])
                window['rd_fab'].update(selected[2])
                window['rd_arrive_date'].update(selected[3])
                window['rd_depart_date'].update(selected[4])
                window['rd_id'].update(selected[5])

                arrive_date = datetime.strptime(selected[3], '%d/%m/%Y').date().strftime('%Y%m%d')
                rd_data = fetch_read_page_data(selected[0], selected[1], arrive_date, selected[5])

                if len(rd_data):
                    window['rd_budget'].update(rd_data[0][0])
                    window['rd_InpImgPath'].update(rd_data[0][1])

                    if rd_data[0][1] and rd_data[0][1] != 'nulo' and rd_data[0][1] != 'nulas' and rd_data[0][1] != '':
                        rows_to_add = create_row(rd_data[0][1])

                        for row in rows_to_add:
                            print(row)
                            window.extend_layout(window['-rd_img_frame-'], [row])
                            window['-rd_img_frame-'].contents_changed()
                    else:
                        window['rd_InpImgPath'].update('sem imagens')
                else:
                    window['rd_budget'].update('sem orçamento')
                    window['rd_InpImgPath'].update('sem imagens')

                window['-SEARCH_LIST_PAGE-'].update(visible=False)
                window['-READ_PAGE-'].update(visible=True)

                state = states.READ


        elif state == states.READ:
            # READ ###################################################
            """TODO:
                    preencher os dados do equipamento
                    mostrar as imagens
            """
            if event == '-btRBack-':
                window['-READ_PAGE-'].update(visible=False)
                window['-SEARCH_PAGE-'].update(visible=True)

                window['rd_client'].update('')
                window['rd_equip'].update('')
                window['rd_fab'].update('')
                window['rd_arrive_date'].update('')
                window['rd_depart_date'].update('')
                window['rd_id'].update('')

                for i in range(row_counter):
                    print('delete:',i)
                    window[f'-ROW{i}-'].update(visible=False)

                state = states.SEARCH

            if event == '-btREdit-':
                data_to_fill = fetch_write_page_data()

                window['-inpEClient-'].update(values=data_to_fill[0])
                window['-inpEFab-'].update(values=data_to_fill[1])
                window['-inpEType-'].update(values=data_to_fill[2])

                window['-inpEClient-'].update(window['rd_client'].get())
                window['-inpEType-'].update(window['rd_equip'].get())
                window['-inpEFab-'].update(window['rd_fab'].get())
                window['-inpEID-'].update(window['rd_id'].get())
                window['-inpEBudget-'].update(window['rd_budget'].get())
                window['-EArriveDate-'].update(window['rd_arrive_date'].get())
                window['-EDepartureDate-'].update(window['rd_depart_date'].get())

                window['-READ_PAGE-'].update(visible=False)
                window['-EDIT_PAGE-'].update(visible=True)

                state = states.EDIT_ENTRY

        elif state == states.WRITE:
            # WRITE ##################################################

            if event == '-btWCancel-':
                print('saiiii')
                window['-WRITE_PAGE-'].update(visible=False)
                window['-MAIN_PAGE-'].update(visible=True)

                state = states.MAIN

            if event == '-btWSub-':
                print('adicionar ao banco de dados')

                infos = [('-inpWClient-', values['-inpWClient-']), ('-inpWType-', values['-inpWType-']), ('-inpWFab-', values['-inpWFab-']), ('-inpWBudget-',values['-inpWBudget-'])]
                lack = False

                #window['-inpWClient-'].widget.config(background_color='#ff2929')
                for info in infos:
                    if window[info[0]].__class__ is sg.Combo:
                        combo_style = window[info[0]].ttk_style
                        style_name = window[info[0]].widget["style"]
                        combo_style.configure(style_name, fieldbackground='#ffffff')
                    else:
                        window[info[0]].update(background_color='#ffffff')
                    if info[1].strip() == '':
                        if window[info[0]].__class__ is sg.Combo:
                            combo_style = window[info[0]].ttk_style
                            style_name = window[info[0]].widget["style"]
                            combo_style.configure(style_name, fieldbackground='#ff9999')
                        else:
                            window[info[0]].update(background_color='#ff9999')
                        #window[info[0]].update(background_color='#ff2929')
                        lack = True

                if lack:
                    print("ERRO: preencha os dados")
                    window['-WDisc-'].update('Preencha os dados que faltam', text_color='#ff2929')
                    continue

                images_path = None

                if len(image_files):
                    created = False
                    while not created:
                        if os.path.isdir(storage_folder):
                            year_folder = os.path.join(storage_folder, date.today().strftime('%Y'))

                            if os.path.isdir(year_folder):
                                client_folder = os.path.join(year_folder, values['-inpWClient-'].capitalize())

                                if os.path.isdir(client_folder):
                                    equipment_folder = os.path.join(client_folder, values['-inpWID-'])

                                    if os.path.isdir(equipment_folder):
                                        date_folder = os.path.join(equipment_folder, date.today().strftime('%Y-%m-%d'))

                                        if os.path.isdir(date_folder):
                                            for file_name in image_files:
                                                shutil.copy2(file_name, date_folder)

                                            images_path = date_folder
                                            created = True

                                        else:
                                            os.mkdir(date_folder)

                                    else:
                                        os.mkdir(equipment_folder)

                                else:
                                    os.mkdir(client_folder)

                            else:
                                os.mkdir(year_folder)

                        else:
                            os.mkdir(storage_folder)

                print(images_path)

                query = f"""
                    INSERT INTO Entradas_teste (cliente, tipo, fabricante, id, orcamento, imagens, data_entrada, data_saida)
                    VALUES ('{values['-inpWClient-'].capitalize()}', '{values['-inpWType-'].capitalize()}', '{values['-inpWFab-'].capitalize()}',
                    '{values['-inpWID-']}', '{values['-inpWBudget-']}', '{images_path}', '{date.today().strftime('%Y%m%d')}',
                    NULL) 
                """

                print(query)

                cursor.execute(query)
                cursor.commit()

                window['-WRITE_PAGE-'].update(visible=False)
                window['-MAIN_PAGE-'].update(visible=True)

                state = states.MAIN

            if event == '-btWImg':
                files = filedialog.askopenfiles()
                file_names = ''
                for file in files:
                    image_files.append(file.name)
                    file_names += f"{file.name.split('/')[-1]}\n"
                window['-imgArchivesTxt-'].update(file_names)

        elif state == states.EDIT_ENTRY:

            if event == '-btECancel-':

                window['-inpEClient-'].update('')
                window['-inpEType-'].update('')
                window['-inpEFab-'].update('')
                window['-inpEID-'].update('')
                window['-inpEBudget-'].update('')
                window['-EArriveDate-'].update('')
                window['-EDepartureDate-'].update('')

                window['-EDIT_PAGE-'].update(visible=False)
                window['-READ_PAGE-'].update(visible=True)

                state = states.READ

            if event == '-btESub-':

                try:
                    depart_date = f"'{datetime.strptime(window['-EDepartureDate-'].get(), '%d/%m/%Y').date().strftime('%Y%m%d')}'"
                except:
                    depart_date = 'NULL'

                query = f"""UPDATE Entradas_teste
                SET cliente = '{window['-inpEClient-'].get()}',
                tipo = '{window['-inpEType-'].get()}',
                fabricante = '{window['-inpEFab-'].get()}',
                id = '{window['-inpEID-'].get()}',
                orcamento = '{window['-inpEBudget-'].get()}',
                data_entrada = '{datetime.strptime(window['-EArriveDate-'].get(), '%d/%m/%Y').date().strftime('%Y%m%d')}',
                data_saida = {depart_date}
                WHERE id = '{window['rd_id'].get()}' AND cliente = '{window['rd_client'].get()}' 
                AND data_entrada = '{datetime.strptime(window['rd_arrive_date'].get(), '%d/%m/%Y').date().strftime('%Y%m%d')}'
                """

                print(query)

                window['rd_client'].update(window['-inpEClient-'].get())
                window['rd_equip'].update(window['-inpEType-'].get())
                window['rd_fab'].update(window['-inpEFab-'].get())
                window['rd_id'].update(window['-inpEID-'].get())
                window['rd_budget'].update(window['-inpEBudget-'].get())
                window['rd_arrive_date'].update(window['-EArriveDate-'].get())
                window['rd_depart_date'].update(window['-EDepartureDate-'].get())

                cursor.execute(query)
                cursor.commit()

                window['-EDIT_PAGE-'].update(visible=False)
                window['-READ_PAGE-'].update(visible=True)

                window['-inpEClient-'].update('')
                window['-inpEType-'].update('')
                window['-inpEFab-'].update('')
                window['-inpEID-'].update('')
                window['-inpEBudget-'].update('')
                window['-EArriveDate-'].update('')
                window['-EDepartureDate-'].update('')

                state = states.READ






create_main_window()

