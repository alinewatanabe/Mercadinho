from PyQt5 import QtCore, QtGui, QtWidgets
from database import DataBase
from RFID import RFIDReaderThread
import pandas as pd
import time
import sqlite3
import home
import inventory
import register
import self_checkout
import stand_by


class Main(QtWidgets.QMainWindow):
    def __init__(self):
        super(Main, self).__init__()

        self.id_customer = 0
        self.cpf = ""  # Armazena o CPF
        self.phone = ""  # Armazena o telefone
        self.caps_lock = False  # Flag para controle do Caps Lock
        self.caps_inventory = (
            False  # Flag para controle do Caps Lock na janela inventory
        )
        self.active_text_field = None  # Campo de texto atualmente selecionado
        self.rfid_thread = None  # Thread para leitura do RFID
        self.reading_rfid = False  # Flag para controle da leitura do RFID
        self.setupWindows()  # Configuração da janela
        self.rfid_dict = {}
        self.text_field = ""
        self.adding_product_mode = False
        self.removing_product_mode = False
        self.read_RFID = False
        self.flag_checkout = False

        # --------- Configuração dos botões da janela home --------- #
        self.ui_home.BtnCad.clicked.connect(self.HideHomeShowRegister)
        self.ui_home.BtnSLog.clicked.connect(self.HideHomeShowCheckout)
        self.ui_home.btn_entrar.clicked.connect(self.check_login)
        self.keyboard_btnHome()

        # -------------------------------------- Configuração os botões da janela register -------------------------------------- #
        self.ui_register.btnVoltar.clicked.connect(self.HideRegisterShowHome)
        self.ui_register.btn_register.clicked.connect(self.subscribe_costumer)
        self.keyboard_btnRegister()

        self.ui_register.txtNome.mousePressEvent = (
            lambda event: self.set_active_text_field(self.ui_register.txtNome)
        )
        self.ui_register.txtSobrenome.mousePressEvent = (
            lambda event: self.set_active_text_field(self.ui_register.txtSobrenome)
        )
        self.ui_register.txtCPF.mousePressEvent = (
            lambda event: self.set_active_text_field(self.ui_register.txtCPF)
        )
        self.ui_register.txtTel.mousePressEvent = (
            lambda event: self.set_active_text_field(self.ui_register.txtTel)
        )
        self.ui_register.txtEmail.mousePressEvent = (
            lambda event: self.set_active_text_field(self.ui_register.txtEmail)
        )

        # -------------------------------------- Configurar os botões da janela self checkout -------------------------------------- #
        self.ui_self_checkout.pushButton.clicked.connect(self.HideCheckoutShowHome)

        # -------------------------------------- Configurar os botões da janela inventory -------------------------------------- #
        self.ui_inventory.pushButton.clicked.connect(self.HideInventoryShowHome)
        self.ui_inventory.BtnAddProduct.clicked.connect(self.toggle_add_product_mode)
        self.ui_inventory.BtnRmvProduct.clicked.connect(
            self.toggle_removing_product_mode
        )
        self.ui_inventory.pushButton_2.clicked.connect(self.change_product)
        self.ui_self_checkout.btn_checkout.clicked.connect(self.finalizar_checkout)
        self.keyboard_btnInventory()

    # -------------------------------------- Funções relacionadas a janela home -------------------------------------- #
    def keyboard_btnHome(self):
        """Adiciona o digitos ao display"""
        self.ui_home.btn_0.clicked.connect(lambda: self.update_cpf("0"))
        self.ui_home.btn_1.clicked.connect(lambda: self.update_cpf("1"))
        self.ui_home.btn_2.clicked.connect(lambda: self.update_cpf("2"))
        self.ui_home.btn_3.clicked.connect(lambda: self.update_cpf("3"))
        self.ui_home.btn_4.clicked.connect(lambda: self.update_cpf("4"))
        self.ui_home.btn_5.clicked.connect(lambda: self.update_cpf("5"))
        self.ui_home.btn_6.clicked.connect(lambda: self.update_cpf("6"))
        self.ui_home.btn_7.clicked.connect(lambda: self.update_cpf("7"))
        self.ui_home.btn_8.clicked.connect(lambda: self.update_cpf("8"))
        self.ui_home.btn_9.clicked.connect(lambda: self.update_cpf("9"))
        self.ui_home.btn_.clicked.connect(self.clear_cpf)
        self.ui_home.btn_back.clicked.connect(self.backspace_cpf)

    def HideHomeShowRegister(self):
        """Função que esconde a janela home e mostra a janela de cadastro"""
        self.set_window_position(self.window_home, self.window_register)
        self.window_home.hide()
        self.clear_data_fields()
        self.table_inventory()
        if self.window_home.isMaximized():
            self.window_register.showMaximized()
        else:
            self.window_register.resize(self.window_home.size())
            self.window_register.showNormal()

    def HideHomeShowCheckout(self):
        """Função que esconde a janela home e mostra a janela de self checkout"""

        self.set_window_position(self.window_home, self.window_self_checkout)
        self.window_home.hide()
        self.table_checkouts()
        if self.window_home.isMaximized():
            self.window_self_checkout.showMaximized()
        else:
            self.window_self_checkout.resize(self.window_home.size())
            self.window_self_checkout.showNormal()

    def HideHomeShowInventory(self):
        """Função que esconde a janela home e mostra a janela inventory"""
        self.set_window_position(self.window_home, self.window_inventory)
        self.window_home.hide()
        self.clear_data_fields()
        if self.window_home.isMaximized():
            self.window_inventory.showMaximized()
        else:
            self.window_inventory.resize(self.window_home.size())
            self.window_inventory.showNormal()
            db = DataBase()
            db.connect_db()
            db.create_table_customers()  # Cria a tabela de clientes, se não existir
            db.create_table_inventory()  # Cria a tabela de estoque, se não existir
            db.create_rfid_inventory_table()  # Cria a tabela de RFID, se não existir
            db.create_table_orders() # Cria a tabela de vendas, se não existir
            db.close_connection()
        self.table_inventory()
        self.table_customers()
        self.table_sales()

    def update_cpf(self, digit):
        """Função que atualiza o cpf na janela home"""
        if len(self.cpf) < 11:  # Limita o CPF a 11 dígitos
            self.cpf += digit
            formatted_cpf = self.format_cpf(self.cpf)
            self.ui_home.txt_CPF.setText(formatted_cpf)
            self.ui_home.txt_CPF.setAlignment(QtCore.Qt.AlignCenter)

    def format_cpf(self, cpf):
        """Formata o CPF no padrão XXX.XXX.XXX-XX"""
        if len(self.cpf) <= 3:
            return cpf
        elif len(cpf) <= 6:
            return f"{cpf[:3]}.{cpf[3:]}"
        elif len(cpf) <= 9:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:]}"
        else:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

    def clear_cpf(self):
        "Limpa o Display do CPF"
        self.cpf = ""
        self.ui_home.txt_CPF.setText(self.cpf)

    def backspace_cpf(self):
        """Apaga o último dígito do cpf"""
        self.cpf = self.cpf[:-1]
        formatted_cpf = self.format_cpf(self.cpf)
        self.ui_home.txt_CPF.setText(formatted_cpf)
        self.ui_home.txt_CPF.setAlignment(QtCore.Qt.AlignCenter)

    def check_login(self):
        """Analisa o CPF digitado e redireciona para o estoque (ser for o adm), para o self-checkout ou continua na mesma pagina se der erro"""
        self.costumer = DataBase()
        self.costumer.connect_db()
        authentication = self.costumer.check_customer(self.format_cpf(self.cpf))

        if self.format_cpf(self.cpf) == "123.456.789-12":
            self.HideHomeShowInventory()
        else:
            if authentication == "customer":
                self.HideHomeShowCheckout()
            else:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setWindowTitle("Acesso Negado")
                msg.setText("CPF não cadastrado.")
                msg.exec_()
        self.costumer.close_connection

        try:
            print("Entrou no try")
            self.table_customers()
            self.table_inventory()
            self.table_sales()
        except:
            pass

    # -------------------------------------- Funções relacionadas a janela register -------------------------------------- #
    def keyboard_btnRegister(self):
        self.ui_register.key_0.clicked.connect(lambda: self.update_text("0"))
        self.ui_register.key_1.clicked.connect(lambda: self.update_text("1"))
        self.ui_register.key_2.clicked.connect(lambda: self.update_text("2"))
        self.ui_register.key_3.clicked.connect(lambda: self.update_text("3"))
        self.ui_register.key_4.clicked.connect(lambda: self.update_text("4"))
        self.ui_register.key_5.clicked.connect(lambda: self.update_text("5"))
        self.ui_register.key_6.clicked.connect(lambda: self.update_text("6"))
        self.ui_register.key_7.clicked.connect(lambda: self.update_text("7"))
        self.ui_register.key_8.clicked.connect(lambda: self.update_text("8"))
        self.ui_register.key_9.clicked.connect(lambda: self.update_text("9"))
        self.ui_register.key_a.clicked.connect(lambda: self.update_text("a"))
        self.ui_register.key_b.clicked.connect(lambda: self.update_text("b"))
        self.ui_register.key_c.clicked.connect(lambda: self.update_text("c"))
        self.ui_register.key_d.clicked.connect(lambda: self.update_text("d"))
        self.ui_register.key_e.clicked.connect(lambda: self.update_text("e"))
        self.ui_register.key_f.clicked.connect(lambda: self.update_text("f"))
        self.ui_register.key_g.clicked.connect(lambda: self.update_text("g"))
        self.ui_register.key_h.clicked.connect(lambda: self.update_text("h"))
        self.ui_register.key_i.clicked.connect(lambda: self.update_text("i"))
        self.ui_register.key_j.clicked.connect(lambda: self.update_text("j"))
        self.ui_register.key_k.clicked.connect(lambda: self.update_text("k"))
        self.ui_register.key_l.clicked.connect(lambda: self.update_text("l"))
        self.ui_register.key_m.clicked.connect(lambda: self.update_text("m"))
        self.ui_register.key_n.clicked.connect(lambda: self.update_text("n"))
        self.ui_register.key_o.clicked.connect(lambda: self.update_text("o"))
        self.ui_register.key_p.clicked.connect(lambda: self.update_text("p"))
        self.ui_register.key_q.clicked.connect(lambda: self.update_text("q"))
        self.ui_register.key_r.clicked.connect(lambda: self.update_text("r"))
        self.ui_register.key_s.clicked.connect(lambda: self.update_text("s"))
        self.ui_register.key_t.clicked.connect(lambda: self.update_text("t"))
        self.ui_register.key_u.clicked.connect(lambda: self.update_text("u"))
        self.ui_register.key_v.clicked.connect(lambda: self.update_text("v"))
        self.ui_register.key_w.clicked.connect(lambda: self.update_text("w"))
        self.ui_register.key_x.clicked.connect(lambda: self.update_text("x"))
        self.ui_register.key_y.clicked.connect(lambda: self.update_text("y"))
        self.ui_register.key_z.clicked.connect(lambda: self.update_text("z"))
        self.ui_register.key_c_.clicked.connect(lambda: self.update_text("ç"))
        self.ui_register.key_ar.clicked.connect(lambda: self.update_text("@"))
        self.ui_register.key_und.clicked.connect(lambda: self.update_text("_"))
        self.ui_register.key_pt.clicked.connect(lambda: self.update_text("."))
        self.ui_register.key_space.clicked.connect(lambda: self.update_text(" "))
        self.ui_register.key_caps.clicked.connect(self.toggle_caps)
        self.ui_register.key_.clicked.connect(self.backspace_text)

    def HideRegisterShowHome(self):
        """Função que esconde a janela de cadastro e mostra a janela home"""
        self.set_window_position(self.window_register, self.window_home)
        self.window_register.hide()
        self.clear_data_fields()
        if self.window_register.isMaximized():
            self.window_home.showMaximized()
        else:
            self.window_home.resize(self.window_register.size())
            self.window_home.showNormal()

    def update_text(self, key):
        """Função que atualiza o texto na janela de cadastro"""
        if self.active_text_field is not None:
            # Verifica se o Caps Lock está ativo para alternar entre maiúsculas e minúsculas
            if self.caps_lock:
                key = key.upper()
            if self.active_text_field == self.ui_register.txtCPF:
                if (len(self.cpf) < 11) and (key in "0123456789"):
                    self.cpf += key
                    formatted_cpf = self.format_cpf(self.cpf)
                    self.active_text_field.setPlainText(formatted_cpf)
            elif self.active_text_field == self.ui_register.txtTel:
                if (len(self.phone) < 11) and (key in "0123456789"):
                    self.phone += key
                    formatted_phone = self.format_phone(self.phone)
                    self.active_text_field.setPlainText(formatted_phone)
            else:
                current_text = self.active_text_field.toPlainText()
                updated_text = current_text + key
                self.active_text_field.setPlainText(updated_text)

    def eventFilter(self, obj, event):
        """Captura o foco do QTextBrowser e armazena o campo ativo."""
        if event.type() == QtCore.QEvent.FocusIn:
            if obj == self.ui_register.txtNome:
                self.active_text_browser = self.ui_register.txtNome
            elif obj == self.ui_register.txtSobrenome:
                self.active_text_browser = self.ui_register.txtSobrenome
            elif obj == self.ui_register.txtCPF:
                self.active_text_browser = self.ui_register.txtCPF
            elif obj == self.ui_register.txtTel:
                self.active_text_browser = self.ui_register.txtTel
            elif obj == self.ui_register.txtEmail:
                self.active_text_browser = self.ui_register.txtEmail
        return super(Main, self).eventFilter(obj, event)

    def set_active_text_field(self, text_field):
        """Define o campo de texto ativo."""
        self.active_text_field = text_field
        # print(f"Active text field: {self.active_text_field.objectName()}")

    def format_phone(self, phone):
        """Formata o telefone no padrão (XX) XXXXX-XXXX"""
        if len(phone) <= 2:
            return f"({phone}"
        elif len(phone) <= 7:
            return f"({phone[:2]}) {phone[2:]}"
        else:
            return f"({phone[:2]}) {phone[2:7]}-{phone[7:]}"

    def backspace_text(self):
        """Função que remove o último caractere do campo de texto ativo."""
        # print("Backspace was pressed")
        if self.active_text_field is not None:
            if self.active_text_field == self.ui_register.txtCPF:
                self.cpf = self.cpf[:-1]  # Remover o último dígito da variável self.cpf
                formatted_cpf = self.format_cpf(
                    self.cpf
                )  # Atualizar o texto do campo CPF com o formato atualizado
                self.active_text_field.setPlainText(formatted_cpf)
            elif self.active_text_field == self.ui_register.txtTel:
                self.phone = self.phone[:-1]
                formatted_phone = self.format_phone(self.phone)
                self.active_text_field.setPlainText(formatted_phone)
            else:
                current_text = (
                    self.active_text_field.toPlainText()
                )  # Para os outros campos, apenas remover o último caractere
                updated_text = current_text[:-1]
                self.active_text_field.setPlainText(updated_text)

    def toggle_caps(self):
        """Função que alterna o Caps Lock."""
        self.caps_lock = not self.caps_lock

        if self.caps_lock:
            self.ui_register.key_a.setText("A")
            self.ui_register.key_b.setText("B")
            self.ui_register.key_c.setText("C")
            self.ui_register.key_d.setText("D")
            self.ui_register.key_e.setText("E")
            self.ui_register.key_f.setText("F")
            self.ui_register.key_g.setText("G")
            self.ui_register.key_h.setText("H")
            self.ui_register.key_i.setText("I")
            self.ui_register.key_j.setText("J")
            self.ui_register.key_k.setText("K")
            self.ui_register.key_l.setText("L")
            self.ui_register.key_m.setText("M")
            self.ui_register.key_n.setText("N")
            self.ui_register.key_o.setText("O")
            self.ui_register.key_p.setText("P")
            self.ui_register.key_q.setText("Q")
            self.ui_register.key_r.setText("R")
            self.ui_register.key_s.setText("S")
            self.ui_register.key_t.setText("T")
            self.ui_register.key_u.setText("U")
            self.ui_register.key_v.setText("V")
            self.ui_register.key_w.setText("W")
            self.ui_register.key_x.setText("X")
            self.ui_register.key_y.setText("Y")
            self.ui_register.key_z.setText("Z")
            self.ui_register.key_c_.setText("Ç")
            self.ui_register.key_caps.setStyleSheet(
                "QPushButton{\n"
                "border-radius: 7px;\n"
                "background-color: rgb(60, 160, 181);\n"
                "border-style: outset;\n"
                "color: white;\n"
                "}"
            )
        else:
            self.ui_register.key_a.setText("a")
            self.ui_register.key_b.setText("b")
            self.ui_register.key_c.setText("c")
            self.ui_register.key_d.setText("d")
            self.ui_register.key_e.setText("e")
            self.ui_register.key_f.setText("f")
            self.ui_register.key_g.setText("g")
            self.ui_register.key_h.setText("h")
            self.ui_register.key_i.setText("i")
            self.ui_register.key_j.setText("j")
            self.ui_register.key_k.setText("k")
            self.ui_register.key_l.setText("l")
            self.ui_register.key_m.setText("m")
            self.ui_register.key_n.setText("n")
            self.ui_register.key_o.setText("o")
            self.ui_register.key_p.setText("p")
            self.ui_register.key_q.setText("q")
            self.ui_register.key_r.setText("r")
            self.ui_register.key_s.setText("s")
            self.ui_register.key_t.setText("t")
            self.ui_register.key_u.setText("u")
            self.ui_register.key_v.setText("v")
            self.ui_register.key_w.setText("w")
            self.ui_register.key_x.setText("x")
            self.ui_register.key_y.setText("y")
            self.ui_register.key_z.setText("z")
            self.ui_register.key_c_.setText("ç")
            self.ui_register.key_caps.setStyleSheet(
                "QPushButton{\n"
                "border-radius: 7px;\n"
                "background-color: rgb(110, 200, 220);\n"
                "border-style: outset;\n"
                "color: white;\n"
                "}"
            )

    def validate_cpf(self, cpf):
        """Verifica se o CPF é válido ou não"""
        try:
            soma_primeiro_digito = 0
            soma_segundo_digito = 0
            # Removendo os pontos e hífen
            cpf = cpf.replace(".", "")
            cpf = cpf.replace("-", "")

            if (len(cpf) != 11) or (
                cpf == cpf[0] * 11
            ):  # Verificar se o CPF tem um tamanho diferente de 11 dígitos ou se todos os digitos são iguais
                return False

            # ------ Calculando o primeiro dígito verificador ------ #
            for i in range(9):
                soma_primeiro_digito += int(cpf[i]) * (10 - i)
            resto_primeiro_digito = soma_primeiro_digito % 11

            if resto_primeiro_digito < 2:
                primeiro_digito_verif = 0
            else:
                primeiro_digito_verif = 11 - resto_primeiro_digito

            # ------ Calculando o segundo dígito verificador ------ #
            for i in range(10):
                soma_segundo_digito += int(cpf[i]) * (11 - i)
            resto_segundo_digito = soma_segundo_digito % 11

            if resto_segundo_digito < 2:
                segundo_digito_verif = 0
            else:
                segundo_digito_verif = 11 - resto_segundo_digito

            # ------ Comparando os dígitos verificadores calculados com os dígitos do CPF informado ------ #
            if cpf[9] == str(primeiro_digito_verif) and cpf[10] == str(
                segundo_digito_verif
            ):
                return True
            else:
                return False
        except:
            return False

    def subscribe_costumer(self):
        """Função que coleta e imprime os dados do formulário de cadastro"""
        name = self.ui_register.txtNome.toPlainText()
        surname = self.ui_register.txtSobrenome.toPlainText()
        cpf = self.ui_register.txtCPF.toPlainText()
        phone = self.ui_register.txtTel.toPlainText()
        email = self.ui_register.txtEmail.toPlainText()

        if (name == "") or (surname == "") or (cpf == "") or (phone == ""):
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle("Campos Vazios")
            msg.setText("Todos os campos com exceção do email são obrigatórios.")
            msg.exec_()
            return None

        if self.validate_cpf(cpf):
            pass
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle("CPF Inválido")
            msg.setText("O CPF informado é inválido.")
            msg.exec_()
            return None

        db = DataBase()
        db.connect_db()
        db.create_table_customers()
        check = db.insert_customer(name, surname, cpf, phone, email)
        db.close_connection()

        if check == "cpf exists":
            return

        self.clear_data_fields()

        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("Cadastro Realizado")
        msg.setText("Cadastro realizado com sucesso!")
        msg.exec_()

    def clear_data_fields(self):
        """Limpa os campos de texto do formulário de cadastro"""
        self.ui_register.txtNome.setPlainText("")
        self.ui_register.txtSobrenome.setPlainText("")
        self.ui_register.txtCPF.setPlainText("")
        self.ui_register.txtTel.setPlainText("")
        self.ui_register.txtEmail.setPlainText("")
        self.cpf = ""
        self.phone = ""
        self.ui_home.txt_CPF.setText(self.cpf)

    # -------------------------------------- Funções relacionadas a janela self checkout -------------------------------------- #
    def HideCheckoutShowHome(self):
        """Função que esconde a janela de self checkout e mostra a janela home"""
        self.set_window_position(self.window_self_checkout, self.window_home)
        self.window_self_checkout.hide()
        self.rfid_reader_thread.stop()
        self.ui_self_checkout.l_Nptotal.setText("R$ 0.00")
        self.ui_self_checkout.treeWidget.clear()
        self.ui_self_checkout.l_nprod.setText("Produto")
        self.ui_self_checkout.l_Nvunit.setText("R$ 0.00")
        self.ui_self_checkout.l_Nqtd.setText("0")
        self.ui_self_checkout.l_Nvtotal.setText("R$ 0.00")
        if self.window_self_checkout.isMaximized():
            self.window_home.showMaximized()
        else:
            self.window_home.resize(self.window_self_checkout.size())
            self.window_home.showNormal()

    # -------------------------------------- Funções relacionadas a janela inventory -------------------------------------- #
    def change_product(self):
        """Função que altera o produto selecionado"""
        print("Produto alterado.")
        product_id = self.ui_inventory.product_id
        quantity_product = self.ui_inventory.sb_qtd.value()
        product_name = self.ui_inventory.l_nprod.text()
        quantity_alert = self.ui_inventory.sb_qtd_alert.value()
        product_price = self.ui_inventory.ds_pa.value()
        product_price_no_affiliate = self.ui_inventory.ds_psa.value()

        # Transformar , em . para o preço
        product_price = int(product_price)
        quantity_alert = int(quantity_alert)

        db = DataBase()
        db.connect_db()

        if product_name:
            db.update_product(
                product_id,
                product_name,
                quantity_product,
                quantity_alert,
                product_price,
                product_price_no_affiliate,
            )
            self.table_inventory()
        db.close_connection()

    def HideInventoryShowHome(self):
        """Função que esconde a janela inventory e mostra a janela home"""
        self.set_window_position(self.window_home, self.window_inventory)
        self.window_inventory.hide()
        if self.window_inventory.isMaximized():
            self.window_home.showMaximized()
        else:
            self.window_home.resize(self.window_inventory.size())
            self.window_home.showNormal()

    def keyboard_btnInventory(self):
        self.ui_inventory.Btn_0.clicked.connect(lambda: self.update_field("0"))
        self.ui_inventory.Btn_1.clicked.connect(lambda: self.update_field("1"))
        self.ui_inventory.Btn_2.clicked.connect(lambda: self.update_field("2"))
        self.ui_inventory.Btn_3.clicked.connect(lambda: self.update_field("3"))
        self.ui_inventory.Btn_4.clicked.connect(lambda: self.update_field("4"))
        self.ui_inventory.Btn_5.clicked.connect(lambda: self.update_field("5"))
        self.ui_inventory.Btn_6.clicked.connect(lambda: self.update_field("6"))
        self.ui_inventory.Btn_7.clicked.connect(lambda: self.update_field("7"))
        self.ui_inventory.Btn_8.clicked.connect(lambda: self.update_field("8"))
        self.ui_inventory.Btn_9.clicked.connect(lambda: self.update_field("9"))
        self.ui_inventory.Btn_a.clicked.connect(lambda: self.update_field("a"))
        self.ui_inventory.Btn_b.clicked.connect(lambda: self.update_field("b"))
        self.ui_inventory.Btn_c.clicked.connect(lambda: self.update_field("c"))
        self.ui_inventory.Btn_d.clicked.connect(lambda: self.update_field("d"))
        self.ui_inventory.Btn_e.clicked.connect(lambda: self.update_field("e"))
        self.ui_inventory.Btn_f.clicked.connect(lambda: self.update_field("f"))
        self.ui_inventory.Btn_g.clicked.connect(lambda: self.update_field("g"))
        self.ui_inventory.Btn_h.clicked.connect(lambda: self.update_field("h"))
        self.ui_inventory.Btn_i.clicked.connect(lambda: self.update_field("i"))
        self.ui_inventory.Btn_j.clicked.connect(lambda: self.update_field("j"))
        self.ui_inventory.Btn_k.clicked.connect(lambda: self.update_field("k"))
        self.ui_inventory.Btn_l.clicked.connect(lambda: self.update_field("l"))
        self.ui_inventory.Btn_m.clicked.connect(lambda: self.update_field("m"))
        self.ui_inventory.Btn_n.clicked.connect(lambda: self.update_field("n"))
        self.ui_inventory.Btn_o.clicked.connect(lambda: self.update_field("o"))
        self.ui_inventory.Btn_p.clicked.connect(lambda: self.update_field("p"))
        self.ui_inventory.Btn_q.clicked.connect(lambda: self.update_field("q"))
        self.ui_inventory.Btn_r.clicked.connect(lambda: self.update_field("r"))
        self.ui_inventory.Btn_s.clicked.connect(lambda: self.update_field("s"))
        self.ui_inventory.Btn_t.clicked.connect(lambda: self.update_field("t"))
        self.ui_inventory.Btn_u.clicked.connect(lambda: self.update_field("u"))
        self.ui_inventory.Btn_v.clicked.connect(lambda: self.update_field("v"))
        self.ui_inventory.Btn_w.clicked.connect(lambda: self.update_field("w"))
        self.ui_inventory.Btn_x.clicked.connect(lambda: self.update_field("x"))
        self.ui_inventory.Btn_y.clicked.connect(lambda: self.update_field("y"))
        self.ui_inventory.Btn_z.clicked.connect(lambda: self.update_field("z"))
        self.ui_inventory.Btn_c_.clicked.connect(lambda: self.update_field("ç"))
        self.ui_inventory.Btn_ar.clicked.connect(lambda: self.update_field("@"))
        self.ui_inventory.Btn_und.clicked.connect(lambda: self.update_field("_"))
        self.ui_inventory.Btn_pt.clicked.connect(lambda: self.update_field("."))
        self.ui_inventory.Btn_space.clicked.connect(lambda: self.update_field(" "))
        self.ui_inventory.Btn_back.clicked.connect(self.backspace_text2)
        self.ui_inventory.Btn_caps.clicked.connect(self.caps_letters)

    def backspace_text2(self):
        """Função que remove o último caractere do campo de texto ativo."""
        self.text_field = self.text_field[:-1]
        self.ui_inventory.textBrowser_2.setText(self.text_field)

    def update_field(self, key):
        if self.caps_inventory:
            key = key.upper()
        self.text_field += key
        self.ui_inventory.textBrowser_2.setText(self.text_field)

    def caps_letters(self):
        self.caps_inventory = not self.caps_inventory

        if self.caps_inventory:
            self.ui_inventory.Btn_a.setText("A")
            self.ui_inventory.Btn_b.setText("B")
            self.ui_inventory.Btn_c.setText("C")
            self.ui_inventory.Btn_d.setText("D")
            self.ui_inventory.Btn_e.setText("E")
            self.ui_inventory.Btn_f.setText("F")
            self.ui_inventory.Btn_g.setText("G")
            self.ui_inventory.Btn_h.setText("H")
            self.ui_inventory.Btn_i.setText("I")
            self.ui_inventory.Btn_j.setText("J")
            self.ui_inventory.Btn_k.setText("K")
            self.ui_inventory.Btn_l.setText("L")
            self.ui_inventory.Btn_m.setText("M")
            self.ui_inventory.Btn_n.setText("N")
            self.ui_inventory.Btn_o.setText("O")
            self.ui_inventory.Btn_p.setText("P")
            self.ui_inventory.Btn_q.setText("Q")
            self.ui_inventory.Btn_r.setText("R")
            self.ui_inventory.Btn_s.setText("S")
            self.ui_inventory.Btn_t.setText("T")
            self.ui_inventory.Btn_u.setText("U")
            self.ui_inventory.Btn_v.setText("V")
            self.ui_inventory.Btn_w.setText("W")
            self.ui_inventory.Btn_x.setText("X")
            self.ui_inventory.Btn_y.setText("Y")
            self.ui_inventory.Btn_z.setText("Z")
            self.ui_inventory.Btn_c_.setText("Ç")
            self.ui_inventory.Btn_caps.setStyleSheet(
                "QPushButton{\n"
                "border-radius: 7px;\n"
                "background-color: rgb(60, 160, 181);\n"
                "border-style: outset;\n"
                "color: white;\n"
                "}"
            )
        else:
            self.ui_inventory.Btn_a.setText("a")
            self.ui_inventory.Btn_b.setText("b")
            self.ui_inventory.Btn_c.setText("c")
            self.ui_inventory.Btn_d.setText("d")
            self.ui_inventory.Btn_e.setText("e")
            self.ui_inventory.Btn_f.setText("f")
            self.ui_inventory.Btn_g.setText("g")
            self.ui_inventory.Btn_h.setText("h")
            self.ui_inventory.Btn_i.setText("i")
            self.ui_inventory.Btn_j.setText("j")
            self.ui_inventory.Btn_k.setText("k")
            self.ui_inventory.Btn_l.setText("l")
            self.ui_inventory.Btn_m.setText("m")
            self.ui_inventory.Btn_n.setText("n")
            self.ui_inventory.Btn_o.setText("o")
            self.ui_inventory.Btn_p.setText("p")
            self.ui_inventory.Btn_q.setText("q")
            self.ui_inventory.Btn_r.setText("r")
            self.ui_inventory.Btn_s.setText("s")
            self.ui_inventory.Btn_t.setText("t")
            self.ui_inventory.Btn_u.setText("u")
            self.ui_inventory.Btn_v.setText("v")
            self.ui_inventory.Btn_w.setText("w")
            self.ui_inventory.Btn_x.setText("x")
            self.ui_inventory.Btn_y.setText("y")
            self.ui_inventory.Btn_z.setText("z")
            self.ui_inventory.Btn_c_.setText("ç")
            self.ui_inventory.Btn_caps.setStyleSheet(
                "QPushButton{\n"
                "border-radius: 7px;\n"
                "background-color: rgb(110, 200, 220);\n"
                "border-style: outset;\n"
                "color: white;\n"
                "}"
            )

    def table_inventory(self):
        print("Entrou no inventory")
        """Função que exibe os dados do estoque na janela inventory"""
        self.ui_inventory.twInventory.setStyleSheet(
            """
                QTreeWidget {
                    font-family: "Poppins";
                    font-size: 9px;
                }    
                QTreeWidget::item {
                    text-align: center;
                }    
            """
        )

        cn = sqlite3.connect(
            "system.db"
        )  # Conecta ao banco de dados e recupera os dados da tabela inventory
        result = pd.read_sql_query("SELECT * FROM inventory ORDER BY id ASC", cn)
        result = result.values.tolist()
        cn.close()  # Fecha a conexão após a consulta

        self.ui_inventory.twInventory.clear()  # Limpa os dados existentes e adiciona os novos dados
        for item in result:
            string_items = [
                str(value) for value in item
            ]  # Converte todos os valores para string
            self.inventory_field = QtWidgets.QTreeWidgetItem(
                self.ui_inventory.twInventory, string_items
            )

        # Ajusta a largura das colunas automaticamente
        for i in range(
            len(result[0]) if result else 0
        ):  # Usa o número de colunas de `result`
            self.ui_inventory.twInventory.resizeColumnToContents(i)

        # Clear listWidget
        self.ui_inventory.listView.clear()

        cn = sqlite3.connect(
            "system.db"
        )  # Conecta ao banco de dados e recupera os dados da tabela inventory
        result = pd.read_sql_query(
            "SELECT name FROM inventory WHERE quantity_alert >= quantity", cn
        )
        result = result.values.tolist()
        result = [str(item) for item in result]
        print(result)
        # Transformar em qlistwidgetitem
        for item in result:
            # ["['Produto A']"] -> Produto A
            item = item[2:-2]
            listWidgetItem = QtWidgets.QListWidgetItem(item)
            self.ui_inventory.listView.addItem(listWidgetItem)

    def table_customers(self):
        """Função que exibe os dados dos clientes na janela inventory"""
        self.ui_inventory.twCustomers.setStyleSheet(
            """
                QTreeWidget {
                    font-family: "Poppins";
                    font-size: 9px;
                }    
                QTreeWidget::item {
                    text-align: center;
                }    
            """
        )

        cn = sqlite3.connect("system.db")
        result = pd.read_sql_query("SELECT * FROM customers ORDER BY id ASC", cn)
        result = result.values.tolist()

        self.ui_inventory.twCustomers.clear()
        for i in result:
            string_items = [str(item) for item in i]
            self.customers_field = QtWidgets.QTreeWidgetItem(
                self.ui_inventory.twCustomers, string_items
            )

        for i in range(1, 5):
            self.ui_inventory.twCustomers.resizeColumnToContents(i)

    def change_flag_checkout(self):
        self.flag_checkout = True

    def table_sales(self):
        """Função que exibe os dados das vendas na janela inventory"""
        db = DataBase()
        db.connect_db()
        
        self.ui_inventory.treeWidget.setStyleSheet(
            """
                QTreeWidget {
                    font-family: "Poppins";
                    font-size: 9px;
                }    
                QTreeWidget::item {
                    text-align: center;
                }    
            """
        )
        cn = sqlite3.connect(
            "system.db"
        )  # Conecta ao banco de dados e recupera os dados da tabela inventory
        result = pd.read_sql_query("SELECT * FROM orders ORDER BY id ASC", cn)
        result = result.values.tolist()
        cn.close()  # Fecha a conexão após a consulta

        self.ui_inventory.treeWidget.clear()  # Limpa os dados existentes e adiciona os novos dados
        for item in result:
            string_items = [str(value) for value in item]
            if item[1] == -1:
                string_items[1] = "Cliente não cadastrado"
            else:
                string_items[1] = db.get_name_by_id(item[1])
            self.sales_field = QtWidgets.QTreeWidgetItem(
                self.ui_inventory.treeWidget, string_items
            )

    def table_checkouts(self):
        self.sale = {
            "products": [],
            "total": 0,
        }
        self.rfid_reader_thread = RFIDReaderThread(self)
        self.rfid_reader_thread.rfid_read.connect(self.iniciar_checkout)
        self.rfid_reader_thread.start()
        """Função que exibe os dados dos self checkouts na janela self checkout"""
        # Pegar a ultima venda efetuada

    def toggle_add_product_mode(self):
        """Alterna o estado do botão e o modo de adicionar produtos."""
        if self.adding_product_mode:
            self.adding_product_mode = False
            self.ui_inventory.BtnAddProduct.setStyleSheet(
                "QPushButton{\n"
                "border-radius: 7px;\n"
                "background-color: rgb(110, 200, 220);\n"
                "border-style: outset;\n"
                "color: white;\n"
                "}"
            )
            print("Modo de adicionar produto desativado.")
            self.rfid_reader_thread.stop()
        else:
            if self.removing_product_mode:
                self.toggle_removing_product_mode()

            self.adding_product_mode = True
            self.ui_inventory.BtnAddProduct.setStyleSheet(
                "QPushButton{\n"
                "border-radius: 7px;\n"
                "background-color: rgb(60, 160, 181);\n"
                "border-style: outset;\n"
                "color: white;\n"
                "}"
            )
            print("Modo de adicionar produto ativado.")
            self.start_rfid_reading()
            self.reading_rfid = False

    def toggle_removing_product_mode(self):
        """Alterna o modo de remoção de produto."""
        if self.removing_product_mode:
            self.removing_product_mode = False
            self.ui_inventory.BtnRmvProduct.setStyleSheet(
                "QPushButton{\n"
                "border-radius: 7px;\n"
                "background-color: rgb(110, 200, 220);\n"
                "border-style: outset;\n"
                "color: white;\n"
                "}"
            )
            print("Modo de remover produto desativado.")
            self.rfid_reader_thread.stop()
        else:
            if self.adding_product_mode:
                self.toggle_add_product_mode()

            self.removing_product_mode = True
            self.ui_inventory.BtnRmvProduct.setStyleSheet(
                "QPushButton{\n"
                "border-radius: 7px;\n"
                "background-color: rgb(60, 160, 181);\n"
                "border-style: outset;\n"
                "color: white;\n"
                "}"
            )
            print("Modo de remover produto ativado.")
            self.start_rfid_reading()
            self.reading_rfid = False

    # -------------------------------------- Funções relacionadas a leitura rfid -------------------------------------- #
    def start_rfid_reading(self):
        """Inicia a leitura do RFID em uma thread separada."""
        self.rfid_reader_thread = RFIDReaderThread(self)
        self.rfid_reader_thread.rfid_read.connect(self.process_rfid)
        self.rfid_reader_thread.start()

    def iniciar_checkout(self, rfid_code):
        # Define o cliente se houver um resultado
        # resetar a leitura do rfid
        db = DataBase()
        db.connect_db()
        self.last_product = None
        # checar para ver se o cliente tem cadastro
        cn = sqlite3.connect("system.db")
        result = pd.read_sql_query(
            f"SELECT * FROM customers WHERE cpf = '{self.format_cpf(self.cpf)}'", cn
        )
        if result.empty:
            self.id_customer = -1
        else:
            self.id_customer = result["id"].values[0]
        # Configura o temporizador para atualizar a verificação de produtos
        self.checkout_timer = QtCore.QTimer()
        self.checkout_timer.timeout.connect(lambda: self.atualizar_produto(rfid_code))
        self.checkout_timer.start(100)  # Intervalo de 100ms para verificar produtos

    def atualizar_produto(self, rfid_code):
        db = DataBase()
        db.connect_db()
        if rfid_code == "":
            return
        product = db.get_product_by_rfid(rfid_code)
        # Verificação para garantir que o produto mudou
        if product == getattr(self, "last_product", None):
            return  # Sai da função se for o mesmo produto

        self.last_product = product

        if product:
            # Verifica se o produto já está na lista de vendas
            existing_product = next(
                (
                    item
                    for item in self.sale["products"]
                    if item["name"] == product["name"]
                ),
                None,
            )

            if existing_product:
                print(f"Produto {product['name']} já está na venda.")
                existing_product["quantity"] += 1
                existing_product["total"] = (
                    existing_product["quantity"] * existing_product["price"]
                )
                self.ui_self_checkout.l_Nqtd.setText(str(existing_product["quantity"]))
                self.ui_self_checkout.l_Nvtotal.setText(
                    f"R$ {existing_product['total']:.2f}"
                )
            else:
                print(f"Produto {product['name']} adicionado à venda.")
                new_product = {
                    "id": product["id"],
                    "name": product["name"],
                    "quantity": 1,
                    "price": (
                        product["price_affiliate"]
                        if self.id_customer != -1
                        else product["price_no_affiliate"]
                    ),
                    "total": (
                        product["price_affiliate"]
                        if self.id_customer != -1
                        else product["price_no_affiliate"]
                    ),
                }
                self.sale["products"].append(new_product)
                self.ui_self_checkout.l_nprod.setText(new_product["name"])
                self.ui_self_checkout.l_Nvunit.setText(f"R$ {new_product['price']:.2f}")
                self.ui_self_checkout.l_Nqtd.setText("1")
                self.ui_self_checkout.l_Nvtotal.setText(
                    f"R$ {new_product['total']:.2f}"
                )

            # Atualiza o total da venda
            self.sale["total"] = sum(item["total"] for item in self.sale["products"])
            self.ui_self_checkout.l_Nptotal.setText(f"R$ {self.sale['total']:.2f}")

            # Imprime a lista de produtos para verificar persistência
            print("Lista de produtos atualizada:", self.sale["products"])

            # Atualiza a tabela de vendas
            self.ui_self_checkout.treeWidget.clear()
            for item in self.sale["products"]:
                string_items = [
                    str(value) for key, value in item.items() if key != "id"
                ]
                QtWidgets.QTreeWidgetItem(
                    self.ui_self_checkout.treeWidget, string_items
                )

    def finalizar_checkout(self):
        # Para o temporizador quando o botão de checkout é pressionado
        self.checkout_timer.stop()
        db = DataBase()
        db.connect_db()
        id_customer = self.id_customer
        
        orders = db.get_orders()
        id_sale = orders[-1][0] + 1 if orders else 1
        
        for item in self.sale["products"]:
            db.insert_order(id_sale, id_customer, item["id"], item["quantity"], item["total"])
            db.update_inventory_quantity(item["id"], -item["quantity"])

        db.close_connection()
        # voltar para a tela de home
        # matar a thread de leitura de rfid
        self.sale = {
            "products": [],
            "total": 0,
        }
        
        self.HideCheckoutShowHome()
        print("Checkout finalizado.")

    def process_rfid(self, rfid_code):
        """Processa o RFID lido: incrementa ou diminui a quantidade do produto existente."""
        print(f"RFID lido: {rfid_code}")

        if (not self.reading_rfid):
            self.reading_rfid = True
            db = DataBase()
            db.connect_db()

            if (self.adding_product_mode):
                print("Modo de adicionar produto está ativado")
                product = db.get_product_by_rfid(rfid_code)
                print(product)
                if (product):
                    current_quantity = product['quantity']
                    new_quantity = current_quantity + 1
                    db.update_inventory_quantity(product['id'], 1) 
                    self.table_inventory()
                    print(f"Quantidade do produto com RFID {rfid_code} incrementada para {new_quantity}.")
                else:
                    name = self.ui_inventory.textBrowser_2.toPlainText()
                    if name:
                        print(f"name: {name}")
                        db.add_new_product_from_rfid(rfid_code, name = name, quantity = 1, quantity_alert= 0, price_affiliate = 0.0, price_no_affiliate = 0.0)
                        self.table_inventory()
                        print(f"Novo produto '{name}' adicionado ao estoque com RFID {rfid_code}.")
                    else:
                        print("Erro: Nome do produto está vazio. Não foi possível adicionar o novo produto.")
                        QtWidgets.QMessageBox.warning(self, "Nome do Produto Vazio", "Por favor, insira um nome para o produto antes de adicionar.")

            elif (self.removing_product_mode):
                print("Modo de remover produto está ativado. Processando RFID para remoção...")
                product = db.get_product_by_rfid(rfid_code)

                if (product):
                    current_quantity = product['quantity']
                    if current_quantity > 0:
                        new_quantity = current_quantity - 1
                        db.update_inventory_quantity(product['id'], -1)  
                        self.table_inventory()
                        print(f"Quantidade do produto com RFID {rfid_code} decrementada para {new_quantity}.")
                    else:
                        print("Quantidade insuficiente para remoção.")
                        #QtWidgets.QMessageBox.warning(self, "Quantidade Insuficiente", "Não é possível remover a quantidade, pois está zerada.")
                else:
                    print(f"Erro: Nenhum produto encontrado com RFID {rfid_code}.")
                    # QtWidgets.QMessageBox.warning(self, "Produto Não Encontrado", f"Nenhum produto vinculado ao RFID {rfid_code} foi encontrado para remoção.")

            else:
                print("Nenhum modo de adicionar ou remover está ativado. Ignorando leitura de RFID.")

            db.close_connection()
            self.table_inventory()

            # Reinicia a flag de leitura após um intervalo
            QtCore.QTimer.singleShot(1000, self.reset_reading_flag)
        else:
            print("Leitura de RFID em andamento. Ignorando demais leituras...")

    def reset_reading_flag(self):
        """Reseta a flag de leitura de RFID para permitir novas leituras."""
        self.reading_rfid = False

    # -------------------------------------- Funções auxiliares -------------------------------------- #
    def set_window_position(self, current_window, new_window):
        """Define a posição da nova janela com base na posição da janela atual"""
        pos = current_window.pos()
        new_window.move(pos)

    def setupWindows(self):
        # -------------------------------------- Configurando a janela principal home -------------------------------------- #
        self.window_home = QtWidgets.QMainWindow()
        self.ui_home = home.Ui_MainWindow()
        self.ui_home.setupUi(self.window_home)
        self.window_home.setWindowTitle("Mercadinho")
        icon = QtGui.QIcon("UI_Files/Images/Logo.png")
        self.window_home.setWindowIcon(icon)
        self.window_home.show()

        # -------------------------------------- Configurando a janela inventory -------------------------------------- #
        self.window_inventory = QtWidgets.QWidget()
        self.ui_inventory = inventory.Ui_Form()
        self.ui_inventory.setupUi(self.window_inventory)
        self.window_inventory.setWindowIcon(icon)
        self.window_inventory.setWindowTitle("Mercadinho")

        # -------------------------------------- Configurando a janela de cadastro -------------------------------------- #
        self.window_register = QtWidgets.QWidget()
        self.ui_register = register.Ui_Form()
        self.ui_register.setupUi(self.window_register)
        self.window_register.setWindowIcon(icon)
        self.window_register.setWindowTitle("Mercadinho")

        # -------------------------------------- Configurando a janela self checkout -------------------------------------- #
        self.window_self_checkout = QtWidgets.QWidget()
        self.ui_self_checkout = self_checkout.Ui_Form()
        self.ui_self_checkout.setupUi(self.window_self_checkout)
        self.window_self_checkout.setWindowIcon(icon)
        self.window_self_checkout.setWindowTitle("Mercadinho")

        # -------------------------------------- Configurar a janela de stand by -------------------------------------- #
        self.window_stand_by = QtWidgets.QWidget()
        self.ui_stand_by = stand_by.Ui_Form()
        self.ui_stand_by.setupUi(self.window_stand_by)
        self.window_stand_by.setWindowIcon(icon)
        self.window_stand_by.setWindowTitle("Mercadinho")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    main_window = Main()
    sys.exit(app.exec_())
