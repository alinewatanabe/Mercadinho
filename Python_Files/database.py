from PyQt5 import QtCore, QtGui, QtWidgets
import sqlite3


class DataBase:
    def __init__(self, name="system.db") -> None:
        self.name = name

    def connect_db(self):
        """Cria a conexão com o banco de dados"""
        self.connection = sqlite3.connect(self.name)

    def close_connection(self):
        """Encerra a conexão com o banco de dados"""
        try:
            self.connection.close()
        except:
            pass

    # ------------------- Tabela Clientes ------------------- #
    def create_table_customers(self):
        """Cria a tabela clientes"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                        CREATE TABLE IF NOT EXISTS customers (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            surname TEXT NOT NULL,
                            cpf TEXT UNIQUE NOT NULL,
                            phone TEXT NOT NULL,
                            email TEXT DEFAULT '-'
                        );
                        """
            )
            self.connection.commit()  # Confirma a transação
        except AttributeError:
            print("Faça a conexão")

    def insert_customer(self, name, surname, cpf, phone, email="-"):
        """Adiciona um cliente a tabela"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                            INSERT INTO customers(name, surname, cpf, phone, email) VALUES (?, ?, ?, ?, ?)
                            """,
                (name, surname, cpf, phone, email),
            )
            self.connection.commit()
            return "success"
        except sqlite3.IntegrityError:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle("Erro de Cadastro")
            msg.setText("CPF já cadastrado.")
            msg.exec_()
            return "cpf exists"

    def check_customer(self, cpf):
        """Verifica se o cliente ja existe na tabela"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                           SELECT * FROM customers;
                           """
            )
            for line in cursor.fetchall():
                if line[3] == cpf:
                    return "customer"
                else:
                    continue
            return "Sem Acesso"
        except:
            pass

    # ------------------- Tabela Estoque ------------------- #
    def create_table_inventory(self):
        """Cria a tabela estoque"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                         CREATE TABLE IF NOT EXISTS inventory (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL UNIQUE,
                            quantity INTEGER NOT NULL,
  							quantity_alert REAL,
                            price_affiliate REAL NOT NULL,
                            price_no_affiliate REAL NOT NULL
                        	)
                        """
            )
            self.connection.commit()
        except AttributeError:
            print("Faça a conexão")

    def insert_inventory_data(self, data):
        """Insere os dados na tabela estoque"""
        cursor = self.connection.cursor()

        table_fields = (
            "ID",
            "Nome",
            "Quantidade",
            "Quantidade Alerta",
            "Preço Afiliado (R$)",
            "Preço sem Afiliação (R$)",
        )
        query = f"""INSERT INTO inventory {table_fields} VALUES (?, ?, ? ,?, ?, ?)"""

        try:
            for line in data:
                cursor.execute(query, tuple(line))
                self.connection.commit()

        except sqlite3.IntegrityError:
            print("Erro")

    # ------------------- Tabela RFID ------------------- #
    def create_rfid_inventory_table(self):
        """Cria a tabela rfid_inventory para armazenar produtos relacionados a RFIDs"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS rfid_inventory (
                    rfid_tag TEXT PRIMARY KEY,   -- Código do RFID
                    product_id INTEGER,          -- ID do produto relacionado
                    FOREIGN KEY (product_id) REFERENCES inventory(id) ON DELETE CASCADE
                );
            """
            )
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Erro ao criar tabela RFID: {e}")

    def insert_rfid_data(self, product_id, rfid_tag):
        """Insere dados na tabela de RFID vinculando um produto a uma tag."""
        cursor = self.connection.cursor()
        query = """INSERT INTO rfid_inventory (product_id, rfid_tag) VALUES (?, ?)"""

        try:
            cursor.execute(query, (product_id, rfid_tag))
            self.connection.commit()

        except sqlite3.IntegrityError:
            print("Erro: Tag RFID já cadastrada.")

    def get_product_by_rfid(self, rfid_tag):
        """Busca o produto relacionado ao RFID"""
        query = """
            SELECT inventory.*
            FROM rfid_inventory
            JOIN inventory ON rfid_inventory.product_id = inventory.id
            WHERE rfid_inventory.rfid_tag = ?
        """

        cursor = self.connection.cursor()
        cursor.execute(query, (rfid_tag,))
        product = cursor.fetchone()

        if product:
            return {
                "id": product[0],
                "name": product[1],
                "quantity": product[2],
                "quantity_alert": product[3],
                "price_affiliate": product[4],
                "price_no_affiliate": product[5],
            }
        else:
            return None

    def product_exists(self, name):
        """Verifica se um produto com o mesmo nome já existe no banco de dados."""
        query = "SELECT COUNT(*) FROM inventory WHERE name = ?"
        cursor = self.connection.cursor()
        cursor.execute(query, (name,))
        exists = cursor.fetchone()[0]
        return exists > 0

    def update_product(
        self,
        product_id,
        name,
        quantity,
        quantity_alert,
        price_affiliate,
        price_no_affiliate,
    ):
        """Atualiza um produto no banco de dados."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                UPDATE inventory
                SET name = ?, quantity = ?, quantity_alert = ?, price_affiliate = ?, price_no_affiliate = ?
                WHERE id = ?
            """,
                (
                    name,
                    quantity,
                    quantity_alert,
                    price_affiliate,
                    price_no_affiliate,
                    product_id,
                ),
            )
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Erro ao atualizar produto: {e}")

    def update_inventory_quantity(self, product_id, change):
        """Atualiza a quantidade de um produto no estoque."""
        try:
            cursor = self.connection.cursor()
            # Consulta a quantidade atual do produto
            cursor.execute("SELECT quantity FROM inventory WHERE id = ?", (product_id,))
            current_quantity = cursor.fetchone()

            if current_quantity is None:
                print("Produto não encontrado.")
                return

            # Atualiza a quantidade com base na mudança (pode ser positiva ou negativa)
            new_quantity = current_quantity[0] + change

            if new_quantity < 0:
                print("Quantidade insuficiente em estoque.")
                return

            # Atualiza a quantidade no banco de dados
            cursor.execute(
                "UPDATE inventory SET quantity = ? WHERE id = ?",
                (new_quantity, product_id),
            )
            self.connection.commit()

            print(f"Estoque atualizado com sucesso! Nova quantidade: {new_quantity}")
        except sqlite3.Error as e:
            print(f"Erro ao atualizar a quantidade no estoque: {e}")

    def add_new_product_from_rfid(
        self,
        rfid_tag,
        name,
        quantity,
        quantity_alert,
        price_affiliate,
        price_no_affiliate,
    ):
        """Adiciona um novo produto ou incrementa quantidade no estoque e mapeia o RFID"""
        try:
            cursor = self.connection.cursor()

            # Primeiro, verificar se um produto com o mesmo nome já existe
            cursor.execute("SELECT id, quantity FROM inventory WHERE name = ?", (name,))
            existing_product = cursor.fetchone()

            if existing_product:
                # Se o produto já existe, atualiza a quantidade e mapeia o RFID
                product_id = existing_product[0]
                new_quantity = existing_product[1] + quantity

                cursor.execute(
                    "UPDATE inventory SET quantity = ? WHERE id = ?",
                    (new_quantity, product_id),
                )
                print(f"Quantidade atualizada para o produto '{name}': {new_quantity}")

                # Verificar se o RFID já está mapeado para este produto
                cursor.execute(
                    "SELECT * FROM rfid_inventory WHERE rfid_tag = ?", (rfid_tag,)
                )
                if not cursor.fetchone():
                    # Mapear o RFID para o produto existente
                    cursor.execute(
                        "INSERT INTO rfid_inventory (rfid_tag, product_id) VALUES (?, ?)",
                        (rfid_tag, product_id),
                    )
                    print(f"RFID {rfid_tag} vinculado ao produto existente '{name}'.")

            else:
                # Se o produto não existe, adiciona-o ao inventário e mapeia o RFID
                cursor.execute(
                    """
                    INSERT INTO inventory (name, quantity, quantity_alert, price_affiliate, price_no_affiliate)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (name, quantity, quantity_alert, price_affiliate, price_no_affiliate),
                )

                product_id = cursor.lastrowid  # Obtém o ID do novo produto

                # Mapeia o RFID com o novo produto
                cursor.execute(
                    "INSERT INTO rfid_inventory (rfid_tag, product_id) VALUES (?, ?)",
                    (rfid_tag, product_id),
                )
                print(
                    f"Novo produto '{name}' adicionado ao estoque com RFID {rfid_tag}."
                )

            # Confirma todas as mudanças
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Erro ao adicionar novo produto: {e}")

        finally:
            cursor.close()

    # ------------------- Tabela Pedido ------------------- #
    def create_table_orders(self):
        """Cria a tabela pedidos"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                        CREATE TABLE IF NOT EXISTS orders (
                            id INTEGER,
                            id_costumer INTEGER NOT NULL,
                            id_product INTEGER NOT NULL,
                            quantity INTEGER NOT NULL,
                            price REAL NOT NULL,
                            FOREIGN KEY (id_costumer) REFERENCES customers(id),
                            FOREIGN KEY (id_product) REFERENCES inventory(id)
                        );
                        """
            )
            self.connection.commit()
        except AttributeError:
            print("Faça a conexão")

    def get_name_by_id(self, id):
        """Retorna o nome do cliente pelo ID"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM customers WHERE id = ?", (id,))
        return cursor.fetchone()[0]
    
    def get_orders(self):
        """Retorna todos os pedidos da tabela"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM orders ORDER BY id ASC")
        return cursor.fetchall()
    
    def insert_order(self, id_sale, id_costumer, id_product, quantity, price):
        """Insere um pedido na tabela"""

        id_costumer = int(id_costumer)
        cursor = self.connection.cursor()
        cursor.execute(
            """
                        INSERT INTO orders(id, id_costumer, id_product, quantity, price) VALUES (?,?,?,?,?)
                        """,
            (id_sale, id_costumer, id_product, quantity, price),
        )
        self.connection.commit()

    # ------------------- Tabela Self Checkout ------------------- #
    def create_table_self_checkout(self):
        """Cria a tabela self_checkout"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS self_checkout (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name_product TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    total_price REAL NOT NULL,
                    customer_id INTEGER,  -- NULL para clientes não logados
                    FOREIGN KEY (customer_id) REFERENCES customers(id)  -- Relaciona com a tabela de clientes
                );
            """
            )
            self.connection.commit()
        except AttributeError:
            print("Faça a conexão")

    def insert_checkout(self, name_product, quantity, price, total_price):
        """Insere um produto na tabela de self-checkout"""
        cursor = self.connection.cursor()
        cursor.execute(
            """
                        INSERT INTO self_checkout(name_product, quantity, price, totalprice) VALUES (?, ?, ?, ?)
                        """,
            (name_product, quantity, price, total_price),
        )
        self.connection.commit()


# if __name__ == "__main__":
#     db = DataBase()
#     db.connect_db()
#     db.create_table_customers()
#     db.close_connection()
