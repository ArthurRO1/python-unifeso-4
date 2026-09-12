import threading
import queue
import time

fila_requisicoes = queue.Queue()
fila_respostas = queue.Queue()

def servidor():
    while True:
        if not fila_requisicoes.empty():
            mensagem, cliente_id = fila_requisicoes.get()
            print(f"\n[SERVIDOR] Mensagem recebida de Cliente {cliente_id}: {mensagem}")

            if mensagem.lower() == "hora":
                resposta = time.strftime("%H:%M:%S")
            elif mensagem.lower() == "serviços":
                resposta = "Comandos disponiveis: HORA, SERVIÇOS, SAIR"
            elif mensagem.lower() == "sair":
                resposta = "Encerrando conexão..."
            else:
                resposta = "Comando inválido. Digite HORA, SERVIÇOS ou SAIR."
                
            time.sleep(1)  # Simula algum processamento
            fila_respostas.put((resposta, cliente_id))
            
            
def cliente_interativo(cliente_id):
    while True:
        mensagem = input(f"\n[Cliente {cliente_id}] Digite uma mensagem (HORA, SERVIÇOS, SAIR): ")
        fila_requisicoes.put((mensagem, cliente_id))
      
        while True:
            if not fila_respostas.empty():
                resposta, cid = fila_respostas.get()
                if cid == cliente_id:
                    print(f"[Cliente {cliente_id}] Resposta do servidor: {resposta}")
                    break
                else:
                    fila_respostas.put((resposta, cid))  # Coloca de volta na fila se não for para este cliente
                    
                    if mensagem.lower() == "sair":
                        print(f"[Cliente {cliente_id}] Encerrando cliente.")
                        break
                    
threading.Thread(target=servidor, daemon=True).start()

cliente_interativo(1)