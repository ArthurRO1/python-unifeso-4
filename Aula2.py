import psutil
import pandas as pd
import matplotlib.pyplot as plt

#Obter lista de processos em suas informações
processes = []
for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
    try:
        processes.append(proc.info)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

#Criar um DataFrame
df = pd.DataFrame(processes)

#ordernar pelos que mais consomem a CPU
df_cpu = df.sort_values(by='cpu_percent', ascending=False).head(10)
df_mem = df.sort_values(by='memory_percent', ascending=False).head(10)

#Graficos de CPU
plt.figure(figsize=(12, 5))
plt.barh(df_cpu['name'], df_cpu['cpu_percent'], color='orange')
plt.xlabel('Uso de CPU (%)')
plt.ylabel('Processos')
plt.title('Top 10 Processos por Uso de CPU')
plt.gca().invert_yaxis()
plt.show()

#grafico de memoria 
plt.figure(figsize=(12, 5))
plt.barh(df_mem['name'], df_mem['memory_percent'], color='green')
plt.xlabel('Uso de Memória (%)')
plt.ylabel('Processos')
plt.title('Top 10 Processos por Uso de Memória')   
plt.gca().invert_yaxis()
plt.show()