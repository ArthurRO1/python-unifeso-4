import os
if os.path.exists("fintech.db"):
    os.remove("fintech.db")
    
    import sqlite3
    from dataclasses import dataclass
    
    #-------------------------------
    #--------infra estrutura--------
    #-------------------------------
    
    class Database:
        def __init__(self, db_name="fintech.db"):
            self.conn = sqlite3.connect(db_name)
            self.create_table()
            
        def create_table(self):
            cur = self.conn.cursor()
            cur .execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titular TEXT,
                    saldo REAL
                
            )""")
            self.conn.commit()
            
        def execute(self, query, params=()):
            cur = self.conn.cursor()
            cur.execute(query, params)
            self.conn.commit()
            return cur
            
            
    #-------------------------------
    #Domínio
    #-------------------------------
    
    @dataclass
    class Conta:
        id: int 
        titular: str
        saldo: float = 0.0
        
        def depositar(self, valor: float):
            if valor <= 0:
                raise ValueError("O valor do depósito deve ser positivo.")
            self.saldo += valor
            
        def transferir(self, valor: float, conta_destino):
            if valor <= 0:
                raise ValueError("O valor da transferência deve ser positivo.")
            if self.saldo < valor:
                raise ValueError("Saldo insuficiente para a transferência.")
            self.saldo -= valor
            conta_destino.depositar(valor)
            
#-------------------------------
#Repositório
#-------------------------------

class ContaRepository:
    def __init__(self, db: Database):
        self.db = db
   
    def add(self, conta: Conta):
        cur = self.db.execute(
            "INSERT INTO contas (titular, saldo) VALUES (?, ?)",
            (conta.titular, conta.saldo)
        )
        conta.id = cur.lastrowid
        
    def update(self, conta: Conta):
        self.db.execute(
            "UPDATE contas SET saldo = ? WHERE id = ?",
            (conta.saldo, conta.id)
        )
        
    def get_by_id(self, conta_id: int) -> Conta:
        cur = self.db.execute(
            "SELECT id, titular, saldo FROM contas WHERE id = ?",
            (conta_id,)
        )
        row = cur.fetchone()
        if row:
            return Conta(id=row[0], titular=row[1], saldo=row[2])
        return None

#-------------------------------
#APLICAÇÃO
#-------------------------------

class ContaService:
    def __init__(self, repo: ContaRepository):
        self.repo = repo
        
    def criar_conta(self, titular: str) -> Conta:
        conta = Conta(id=0, titular=titular, saldo=0.0)
        self.repo.add(conta)
        return conta
    
    def depositar(self, conta_id: int, valor: float):
        conta = self.repo.get_by_id(conta_id)
        if not conta:
            raise ValueError("Conta não encontrada.")
        conta.depositar(valor)
        self.repo.update(conta)
        
    def transferir(self, origem_id: int, destino_id: int, valor: float):
        origem = self.repo.get_by_id(origem_id)
        destino = self.repo.get_by_id(destino_id)
        
        if not origem or not destino:
            raise ValueError("Conta de origem ou destino não encontrada.")
        
        origem.transferir(valor, destino)
        
        self.repo.update(origem)
        self.repo.update(destino)
        
#-------------------------------
#APRESENTAÇÃO
#-------------------------------

def menu():
    db = Database()
    repo = ContaRepository(db)
    service = ContaService(repo)
    
    while True:
        print("\nFINTECH:")
        print("1. Criar Conta")
        print("2. Depositar")
        print("3. Transferir")
        print("4. Consultar Conta")
        print("0. Sair")
        op = input("Escolha uma opção: ")
        
        try:
            if op == "1":
                titular = input("Digite o nome do titular: ")
                conta = service.criar_conta(titular)
                print(f"Conta criada com ID: {conta.id}")
                
            elif op == "2":
                conta_id = int(input("ID da conta: "))
                valor = float(input("valor: "))
                service.depositar(conta_id, valor)
                print("Depósito realizado com sucesso.")
                
            elif op == "3":
                origem_id = int(input("ID da conta de origem: "))
                destino_id = int(input("ID da conta de destino: "))
                valor = float(input("valor: "))
                service.transferir(origem_id, destino_id, valor)
                print("Transferência realizada com sucesso.")
                
            elif op == "4":
                conta_id = int(input("ID da conta: "))
                conta = service.repo.get_by_id(conta_id)
                if conta:
                    print(f"ID: {conta.id}, Titular: {conta.titular}, Saldo: {conta.saldo}")
                else:
                    print("Conta não encontrada.")
                    
            elif op == "0":
                break
            else:
                print("Opção inválida. Tente novamente.")
        except Exception as e:
            print(f"Erro: {e}")
        
        