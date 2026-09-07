import sqlite3
from dataclasses import dataclass


class Database:
    def __init__(self, db_name="fintech.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS contas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titular TEXT NOT NULL,
                saldo REAL NOT NULL DEFAULT 0.0
            )
            """
        )
        self.conn.commit()

    def execute(self, query, params=()):
        cur = self.conn.cursor()
        cur.execute(query, params)
        self.conn.commit()
        return cur


@dataclass
class Conta:
    id: int
    titular: str
    saldo: float = 0.0

    def depositar(self, valor: float):
        if valor <= 0:
            raise ValueError("O valor do depósito deve ser positivo.")
        self.saldo += valor

    def sacar(self, valor: float):
        if valor <= 0:
            raise ValueError("O valor do saque deve ser positivo.")
        if self.saldo < valor:
            raise ValueError("Saldo insuficiente para o saque.")
        self.saldo -= valor

    def transferir(self, valor: float, conta_destino):
        if valor <= 0:
            raise ValueError("O valor da transferência deve ser positivo.")
        if self.saldo < valor:
            raise ValueError("Saldo insuficiente para a transferência.")
        self.saldo -= valor
        conta_destino.depositar(valor)


class ContaRepository:
    def __init__(self, db: Database):
        self.db = db

    def add(self, conta: Conta):
        cur = self.db.execute(
            "INSERT INTO contas (titular, saldo) VALUES (?, ?)",
            (conta.titular, conta.saldo),
        )
        conta.id = cur.lastrowid

    def update(self, conta: Conta):
        self.db.execute(
            "UPDATE contas SET saldo = ? WHERE id = ?",
            (conta.saldo, conta.id),
        )

    def get_by_id(self, conta_id: int):
        cur = self.db.execute(
            "SELECT id, titular, saldo FROM contas WHERE id = ?",
            (conta_id,),
        )
        row = cur.fetchone()
        if row:
            return Conta(id=row[0], titular=row[1], saldo=row[2])
        return None

    def get_all(self):
        cur = self.db.execute(
            "SELECT id, titular, saldo FROM contas ORDER BY id"
        )
        return [Conta(id=row[0], titular=row[1], saldo=row[2]) for row in cur.fetchall()]


class ContaService:
    def __init__(self, repo: ContaRepository):
        self.repo = repo

    def criar_conta(self, titular: str) -> Conta:
        titular = titular.strip()
        if not titular:
            raise ValueError("O titular não pode estar vazio.")

        conta = Conta(id=0, titular=titular, saldo=0.0)
        self.repo.add(conta)
        return conta

    def listar_contas(self):
        return self.repo.get_all()

    def depositar(self, conta_id: int, valor: float):
        conta = self.repo.get_by_id(conta_id)
        if not conta:
            raise ValueError("Conta não encontrada.")

        conta.depositar(valor)
        self.repo.update(conta)
        return conta

    def sacar(self, conta_id: int, valor: float):
        conta = self.repo.get_by_id(conta_id)
        if not conta:
            raise ValueError("Conta não encontrada.")

        conta.sacar(valor)
        self.repo.update(conta)
        return conta

    def transferir(self, origem_id: int, destino_id: int, valor: float):
        origem = self.repo.get_by_id(origem_id)
        destino = self.repo.get_by_id(destino_id)

        if not origem or not destino:
            raise ValueError("Conta de origem ou destino não encontrada.")

        origem.transferir(valor, destino)
        self.repo.update(origem)
        self.repo.update(destino)
        return origem, destino


def menu():
    db = Database()
    repo = ContaRepository(db)
    service = ContaService(repo)

    while True:
        print("\nFINTECH")
        print("1. Criar conta")
        print("2. Depositar")
        print("3. Sacar")
        print("4. Transferir")
        print("5. Consultar conta")
        print("6. Listar contas")
        print("0. Sair")

        opcao = input("Escolha uma opção: ")

        try:
            if opcao == "1":
                titular = input("Digite o nome do titular: ")
                conta = service.criar_conta(titular)
                print(f"Conta criada com sucesso! ID: {conta.id}")

            elif opcao == "2":
                conta_id = int(input("ID da conta: "))
                valor = float(input("Valor do depósito: "))
                conta = service.depositar(conta_id, valor)
                print(f"Depósito realizado com sucesso. Saldo atual: R$ {conta.saldo:.2f}")

            elif opcao == "3":
                conta_id = int(input("ID da conta: "))
                valor = float(input("Valor do saque: "))
                conta = service.sacar(conta_id, valor)
                print(f"Saque realizado com sucesso. Saldo atual: R$ {conta.saldo:.2f}")

            elif opcao == "4":
                origem_id = int(input("ID da conta de origem: "))
                destino_id = int(input("ID da conta de destino: "))
                valor = float(input("Valor da transferência: "))
                origem, destino = service.transferir(origem_id, destino_id, valor)
                print(
                    f"Transferência realizada com sucesso. "
                    f"Origem: R$ {origem.saldo:.2f} | Destino: R$ {destino.saldo:.2f}"
                )

            elif opcao == "5":
                conta_id = int(input("ID da conta: "))
                conta = service.repo.get_by_id(conta_id)
                if conta:
                    print(f"ID: {conta.id} | Titular: {conta.titular} | Saldo: R$ {conta.saldo:.2f}")
                else:
                    contas = service.listar_contas()
                    ids = ", ".join(str(conta.id) for conta in contas)
                    print("Conta não encontrada.")
                    print(f"IDs disponíveis: {ids or 'nenhum'}. Crie uma conta pela opção 1.")

            elif opcao == "6":
                contas = service.listar_contas()
                if not contas:
                    print("Nenhuma conta cadastrada. Crie uma conta pela opção 1.")
                else:
                    for conta in contas:
                        print(
                            f"ID: {conta.id} | Titular: {conta.titular} | "
                            f"Saldo: R$ {conta.saldo:.2f}"
                        )

            elif opcao == "0":
                print("Saindo do sistema...")
                break

            else:
                print("Opção inválida. Tente novamente.")

        except ValueError as e:
            print(f"Erro: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")


if __name__ == "__main__":
    menu()
